# GDAutoBackup
------------
A simple python script to automatically backup files of an app to Google Drive after launch, and restore them back before launch. Basically Steam cloud saves, but with Google Drive.

------------


#Setup
GDAutoBackup requires you to create a project on the Google API Console and create an OAuth2 Client ID to work. Here is how to do it:

1. Go to [APIs Console](https://console.developers.google.com/iam-admin/projects "APIs Console") and make your own project.

2. Search for "Google Drive API", select the entry, and click "Enable".

3. Select ‘Credentials’ from the left menu, click "Create Credentials", select "OAuth client ID".

4. Now, the product name and consent screen need to be set -> click "Configure consent screen" and follow the instructions. Once finished:
	a: Select "Application type" to be Web application.

	b: Enter an appropriate name.

	c: Input http://localhost:8080/ for Authorized redirect URIs.

	d: Click Create.

5. Click "Download JSON" on the right side of Client ID to download client_secret_<really long ID>.json

6. Rename the file to client_secrets.json and place it in the same directory as GDAutoBackup.

------------


# Usage

------------

    GDAutoBackup [-h] [-l AppName]
    -h : Displays default help message
    -l AppName : Specify the app to launch. Requires the app to be added to apps.json beforehand.
    Launching GDAutoBackup without any arguments will put you into editor mode where you can edit apps.json.
    
    

------------

