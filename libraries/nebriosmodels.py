

def get_process(PROCESS=None, PROCESS_ID=None, PARENT=None, kind=None):
    # returns a PROCESS object and created boolean
    if PROCESS is not None:
        return PROCESS, False
    elif PROCESS_ID is not None:
        return Process.objects.get(PROCESS_ID=PROCESS_ID, kind=kind), False
    else:
        if isinstance(PARENT, NebriOSModel):
            PARENT = PARENT.process()
        return Process.objects.create(kind=kind, PARENT=PARENT), True


def cleanup_search_kwargs(cls, kwargs):
    for key, value in kwargs.items():
        if isinstance(value, NebriOSModel) or issubclass(type(value), NebriOSModel):
            if key == "PARENT":
                kwargs[key] = value.process()
            else:
                # value is another object
                # update key to an id field to make searchable
                del kwargs[key]
                kwargs["%s_id" % key] = value.process().PROCESS_ID
        elif key in cls.__FIELDS__:
            field = cls.__FIELDS__[key]
            if isinstance(field, NebriOSReference):
                # we need this check here in case there isn't a referenced object
                # as it won't be picked up by the if
                del kwargs[key]
                if value is None:
                    kwargs["%s_id" % key] = None
    return kwargs


class NebriOSModelCollection(object):

    def __init__(self, field_name, model_instance, model_class):
        self.field_name = field_name
        self.model_instance = model_instance
        self.model_class = model_class

    def __len__(self):
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            return 0
        return len(tmp_list)

    def __getitem__(self, key):
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            return None
        else:
            return self.model_class(PROCESS_ID=tmp_list[key])

    def __setitem__(self, key, value):
        if not isinstance(value, self.model_class):
            raise Exception("%s not a valid %s for field %s" % (value, self.model_class.__name__, self.field_name))
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            tmp_list = [value.PROCESS_ID]
        else:
            tmp_list[key] = value.PROCESS_ID
        self.model_instance.__setitem__('%s_ids' % self.field_name, tmp_list)

    def __delitem__(self, key):
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            tmp_list = []
        else:
            del tmp_list[key]
        self.model_instance.__setitem__('%s_ids' % self.field_name, tmp_list)

    def __iter__(self):
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            raise StopIteration
        else:
            for item in tmp_list:
                yield self.model_class(PROCESS_ID=item)

    def __contains__(self, item):
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            return False
        else:
            if isinstance(item, self.model_class):
                return item.PROCESS_ID in tmp_list
            elif isinstance(item, int) or isinstance(item, long):
                return item in tmp_list
            else:
                return False

    def __repr__(self):
        return str(self)

    def __str__(self):
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            return '[]'
        else:
            verbose_list = []
            for index, item_id in enumerate(tmp_list):
                verbose_list.append(str(self.__getitem__(index)))
            return '[%s]' % ', '.join(verbose_list)

    def append(self, value):
        if not isinstance(value, self.model_class):
            raise Exception("%s not a valid %s for field %s" % (value, self.model_class.__name__, self.field_name))
        tmp_list = self.model_instance.__getitem__('%s_ids' % self.field_name)
        if tmp_list is None:
            tmp_list = [value.PROCESS_ID]
        else:
            tmp_list.append(value.PROCESS_ID)
        self.model_instance.__setitem__('%s_ids' % self.field_name, tmp_list)


class NebriOSField(object):

    def __init__(self, default=None, required=False):
        self.default = default
        self.required = required

    def default_value(self):
        if self.default is None:
            return self.default
        elif callable(self.default):
            return (self.default)()
        else:
            return self.default


class NebriOSReference(NebriOSField):

    def __init__(self, model_class, default=None, required=False):
        # set up the field default and required attrs first
        super(NebriOSReference, self).__init__(default=default, required=required)
        self.model_class = model_class


class NebriOSReferenceList(NebriOSField):

    def __init__(self, model_class, default=None, required=False):
        # set up the field default and required attrs first
        super(NebriOSReferenceList, self).__init__(default=default, required=required)
        self.model_class = model_class


def make_reference_list_get(model_class, field_name):
    def getter(self):
        return NebriOSModelCollection(field_name, self, model_class)
    return getter


def make_reference_list_set(model_class, field_name):
    def setter(self, values):
        if values is None:
            self.__setitem__('%s_ids' % field_name, None)
        collection = NebriOSModelCollection(field_name, self, model_class)
        for value in values:
            # ensure all values match the class for this reference list field
            if not isinstance(value, model_class):
                raise Exception("%s not a valid %s for field %s" % (value, model_class.__name__, field_name))
            if not isinstance(value.PROCESS_ID, int) and not isinstance(value.PROCESS_ID, long):
                value.save()
            collection.append(value)
        return collection
    return setter


def make_reference_get(model_class, field_name):
    def getter(self):
        value = self.__getitem__('%s_id' % field_name)
        if value is None:
            return None
        return model_class(PROCESS_ID=value)
    return getter


def make_reference_set(model_class, field_name):
    def setter(self, value):
        # value is the referenced object
        if value is None:
            self.__setitem__('%s_id' % field_name, None)
            return None
        if not isinstance(value, model_class):
            # ensure the value matches the class for this reference field
            raise Exception("%s not a valid %s for field %s" % (value, model_class.__name__, field_name))
        if not isinstance(value.PROCESS_ID, int) and not isinstance(value.PROCESS_ID, long):
            value.save()
        self.__setitem__('%s_id' % field_name, value.PROCESS_ID)
        return value
    return setter


def make_get(field_name):
    def getter(self):
        return self.__getitem__(field_name)
    return getter


def make_set(field_name):
    def setter(self, value):
        return self.__setitem__(field_name, value)
    return setter


class NebriOSModelMetaClass(type):

    def __new__(cls, name, base, attrs):
        fields = {}
        for key, value in attrs.iteritems():
            if isinstance(value, NebriOSField):
                # every field must be an instance of NebriOSField
                fields[key] = value
                if isinstance(value, NebriOSReference):
                    # if this field is a reference, we need different setter and getter
                    # functions
                    attrs[key] = property(make_reference_get(value.model_class, key),
                                          make_reference_set(value.model_class, key))
                elif isinstance(value, NebriOSReferenceList):
                    attrs[key] = property(make_reference_list_get(value.model_class, key),
                                          make_reference_list_set(value.model_class, key))
                else:
                    attrs[key] = property(make_get(key), make_set(key))
        attrs['__FIELDS__'] = fields
        if 'kind' not in attrs:
            attrs['kind'] = name.lower()
        return type.__new__(cls, name, base, attrs)


class NebriOSModel(object):

    __metaclass__ = NebriOSModelMetaClass

    kind = None

    def __init__(self, PROCESS=None, PROCESS_ID=None, PARENT=None, **kwargs):
        if self.__class__.kind is None:
            raise Exception('Model kind is None')
        # get or create the process for this model and set up the dictionary for later reference
        self.__dict__['PROCESS'], created = get_process(PROCESS=PROCESS, PROCESS_ID=PROCESS_ID, PARENT=PARENT,
                                                        kind=self.__class__.kind)
        setattr(self, 'kind', self.__class__.kind)
        if created:
            for key, field in self.__class__.__FIELDS__.iteritems():
                # set any default values
                setattr(self, key, field.default_value())
        for key, value in kwargs.iteritems():
            # set values that were passed with **kwargs
            setattr(self, key, value)

    def process(self):
        # return the dictionary representation of this Process
        return self.__dict__['PROCESS']

    def __setattr__(self, key, value):
        # try to get the model field named key
        # this is for reference fields
        field = self.__class__.__FIELDS__.get(key, None)
        if field is not None:
            if isinstance(field, NebriOSReference):
                if value is None:
                    return self.process().__setattr__("%s_id" % key, value)
                # set a pointer to the referenced process
                return self.process().__setattr__("%s_id" % key, value.PROCESS_ID)
            if isinstance(field, NebriOSReferenceList):
                if value is None:
                    return self.process().__setattr__("%s_ids" % key, value)
                return self.process().__setattr__("%s_ids" % key, NebriOSModelCollection(field, self, self.__class__))
        # set the key in the Process ORM KVP Bag to value
        return self.process().__setattr__(key, value)

    def __getattr__(self, item):
        # try to get the model field named key
        # this is for reference fields
        field = self.__class__.__FIELDS__.get(item, None)
        if field is not None:
            if isinstance(field, NebriOSReference):
                # this is a reference. find the entry for this id in the process __dict__
                value = self.process().__getattr__("%s_id" % item)
                if value is None:
                    return None
                model_class = field.model_class
                return model_class(PROCESS_ID=value)
            if isinstance(field, NebriOSReferenceList):
                value = self.process().__getattr__("%s_ids" % item)
                if value is None:
                    return []
                return NebriOSModelCollection(field, self, self.__class__)
        # we'll check the process __dict__ for item, so it doesn't matter if
        # item is a field or not
        return self.process().__getattr__(item)

    def __setitem__(self, key, value):
        # try to get the model field named key
        # this is for reference fields
        field = self.__class__.__FIELDS__.get(key, None)
        if field is not None:
            if isinstance(field, NebriOSReference):
                if value is None:
                    return self.process().__setitem__("%s_id" % key, value)
                # set a pointer to the referenced process
                return self.process().__setitem__("%s_id" % key, value.PROCESS_ID)
            if isinstance(field, NebriOSReferenceList):
                if value is None:
                    return self.process().__setitem__("%s_ids" % key, value)
                return self.process().__setitem__("%s_ids" % key, NebriOSModelCollection(field, self, self.__class__))
        # set the key in the Process ORM KVP Bag to value
        return self.process().__setitem__(key, value)

    def __getitem__(self, item):
        # try to get the model field named item
        # this is for reference fields
        field = self.__class__.__FIELDS__.get(item, None)
        if field is not None:
            if isinstance(field, NebriOSReference):
                # this is a reference. find the entry for this id in the process __dict__
                value = self.process().__getitem__("%s_id" % item)
                if value is None:
                    return None
                model_class = field.model_class
                return model_class(PROCESS_ID=value)
            if isinstance(field, NebriOSReferenceList):
                value = self.process().__getitem__("%s_ids" % item)
                if value is None:
                    return []
                return NebriOSModelCollection(field, self, self.__class__)
        # we'll check the process __dict__ for item, so it doesn't matter if
        # item is a field or not
        return self.process().__getitem__(item)

    def save(self):
        for key, field in self.__class__.__FIELDS__.iteritems():
            if field.required and (getattr(self, key) is None):
                # if this field is required and its value isn't specified, set default
                default_value = field.default_value()
                if default_value is not None:
                    setattr(self, key, default_value)
                else:
                    # this field is required and does not have a default value set
                    raise Exception("Field %s is required" % key)
        return self.process().save()

    def delete(self):
        self.process().delete()

    @classmethod
    def get(cls, **kwargs):
        # set the kind kvp so we can filter by model in Processes
        kwargs['kind'] = cls.kind
        kwargs = cleanup_search_kwargs(cls, kwargs)
        p = Process.objects.get(**kwargs)
        return cls(PROCESS=p)

    @classmethod
    def get_or_create(cls, **kwargs):
        # set the kind kvp so we can filter by the correct model
        # and save this as a Process, if needed
        kwargs['kind'] = cls.kind
        kwargs = cleanup_search_kwargs(cls, kwargs)
        try:
            # try to find a matching Process first
            p = Process.objects.get(**kwargs)
            return cls(PROCESS=p), False
        except Process.DoesNotExist:
            # otherwise, try to create with the given arguments
            p = cls(**kwargs)
            p.save()
            return p, True

    @classmethod
    def filter(cls, **kwargs):
        # set the kind kvp so we can filter by model in our Processes
        kwargs['kind'] = cls.kind
        kwargs = cleanup_search_kwargs(cls, kwargs)
        q = Process.objects.filter(**kwargs)
        return [cls(PROCESS=p) for p in q]

    def __str__(self):
        return "<%s id %s>" % (self.__class__.__name__, self.process().PROCESS_ID)

    def __repr__(self):
        return str(self)
