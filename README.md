# trello_webhooks
Trello Webhook App for NebriOS

This app is intended for use in a NebriOS instance. Visit https://nebrios.com to sign up for free!

<h4>Setup</h4>
First install requirements:

```
pip install -U git+https://github.com/koryd-bixly/nebri-trello.git

pip install -r requirements.txt

```

Please setup an instance_settings.py file in your libraries with the following information:
   ```
      INSTANCE_NAME = <instance_name>
      INSTANCE_FQDN = <instance_fully_qualified_domain_name>
      INSTANCE_HTTP_URL = <instance_http_url>
      INSTANCE_HTTPS_URL = <instance_https_url>
      INSTANCE_SSH_IP = <instance_ssh_ip>
      INSTANCE_SSH_PORT = <instance_ssh_port>
      DEFAULT_USER = <your_email>
   ```
Please ensure that all files are placed in the correct places over SFTP. For example, all scripts should go to the /script directory on your instance.
If this is the first time setting up these webhooks, a trello api key/secret pair will need to be supplied. This pair can be acquired at https://trello.com/1/appkey/generate. You must be logged in to trello to generate an app key/secret pair.
You can set the shared KVPs in debug mode as follows:
  ```
  shared.trello_api_key := <api_key>
  shared.trello_api_secret := <api_secret>
  shared.DEFAULT_USER := <your_email>
  ```

Once all files are properly uploaded, this app needs to be set up from debug mode. Make sure that the subject line is clear in Debug mode and input the following:
    ```
    trello_webhook_setup := True
    ```

This will trigger a card load with a link to follow that will provide you with a token generated with your app key/secret. The generated token will be stored for future use.

Once you submit the card, setup is complete. At this point, data will automatically be received from trello based on events that happen on the user's boards and will update appropriate KVPs accordingly. The initial webhook registration can take some time, so please be patient.

Currenty this app supports only one user per instance. If you need to remove an old user, input the following:
    ```
    trello_delete_webhooks_for_user := True
    ```

<h4>Usage</h4>
There are a few different ticket scenarios that are currently covered by this app: automatically posting a template checklist to a board, notifications when  checklist is about to be due,  notifications when a card has become past due, and notifications for when a card has been archived.

Each scenario has it's own rule script to send out notifications or take actions. These rule scripts can be triggered manually for testing, or can be set up to run on a drip schedule.

<strong>Manually Triggering Scripts</strong>
  ```
  trello_overdue_cards_notify := True
  default_user := <your_email>
  ```
  When the above line is sent via debug mode, the `trello_overdue_cards_notify` script will be woken up, causing it to find all overdue cards and send an email listing all cards  and the card creator. An email will be sent to the address defined during setup in the `DEFAULT_USER`.
  
  ```
  trello_checklist_due_soon := True
  ```
  When the above line is sent via debug mode, the `trello_checklist_due_soon` script will be woken up, causing it to find all cards that have an unfinished checklist due in the next past 6 hours. An email will be sent to the address defined during setup in the `DEFAULT_USER`.

  ```
  trello_search_template_checklist := <drip_name>
  ```
  When the above line is sent via debug mode, the `trello_search_template_checklist` script will be woken up, causing it to find all cards that have a label named `template checklist`. This card will be copied to the board and list specified in the description. Here is an example configureation for a template checklist description:
   ```
      due=<how long after crated should the new card be due. OPTIONS: day, hour, week, month, quarter, year>
      board=<board name>
      list=<list name>
      drip=<drip name>
      description=<description on new card>
   ```

   <strong>NOTE:</strong> do not put spaces between the `=` and the key/value

   The drip paramater above is desgined to allow you to have multiple checklists wake up on the same drip. For example, I could create the 8am drip and all cards with `drip=8am` will be copied when the script wakes up. Remember that drip names must be a string and not start with 'RAN'.



<strong>Setting Up a Drip</strong>

Under advanced in the nebrios web app, there is a drips tab. This can also be accessed at the `/core/drip/` endpoint.
Drips utilize cron job syntax for when they are run (www.cronmaker.com):
  ```
   * * * * *  command to execute
   │ │ │ │ │
   │ │ │ │ │
   │ │ │ │ └───── day of week (0 - 6) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
   │ │ │ └────────── month (1 - 12)
   │ │ └─────────────── day of month (1 - 31)
   │ └──────────────────── hour (0 - 23)
   └───────────────────────── min (0 - 59)
  ```
  
  `schedule` should reflect the cron schedule in the above syntax
  `key/value pairs` should reflect what key/value pairs should be created
  
  <strong>Example</strong> In order to create a drip to run `trello_search_template_checklist`, create new cards from all templates on the 8am drip every day at 8am, your drip should look like:
      
      schedule: 0 8 * * *
      key/value pairs: trello_search_template_checklist := 8am
