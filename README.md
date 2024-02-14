# Zammad Front Import Script
Simple Python script using the Zammad API to import past Data from Front.

This script should work for most things, but is definitely not full-featured and does everything on best-effort.

## Usage
1. Login to Zammad. Go to your profile page and get an API token
1. Create the necessary groups in Zammad
1. Enter the Zammad Rails console (depending on your installation there is a different way to do this).
    Then run 
    ```
    Setting.set('import_mode', true)
    Setting.set('system_init_done', false)
    ```
    there
1. Install the dependencies for this python script (e.g. in a venv) with `pip install -r requirements.txt`
1. Get front to send you a dump of your team inboxes (tested with the dump for specific inboxes with attachments)
1. Move the inboxes folder and the `createTickets` python script into your working directory
1. Run the createTickets python script
1. Run in the Zammad Rails console
    ```
    Setting.set('import_mode', false)
    Setting.set('system_init_done', true)
    ```

WARNING: If the script is run multiple times on the same dump IT WILL create DOUBLE TICKETS
