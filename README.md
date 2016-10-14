# LetItRain
**Cloud Storage Positive/Negative Hashing**

## About

This tool will take credentials or an API key for a cloud storage provider as input (Google Drive, Dropbox, etc.) and download all available info (current files, deleted files, and file versions) from that provider. The data will be sorted into an easy-to-navigate directory structure, and both positive and negative hashing will be performed with a user-provided hash database. The tool will report with all matching "bad" hashes as well as which files that can be safely ignored. Available metadata for each file will be downloaded and stored in an easily accessible format.

## Setting Up Your Environment

This application uses OAuth 2.0 to correspond with Google Drive API requirements.

There are a few initial steps that have to happen before using Let It Rain:
1. Install PyDrive
2. Establish Google Drive Credentials

#### Installing PyDrive
This application uses PyDrive, a Python wrapper for Google Drive's API.

Install PyDrive:
```
pip install pydrive
```

#### Google Drive Credentials
Google Drive, to use the API, requires credentials for the account being accessed. In order to get the necessary client_secrets.json file, there are a few required steps.

* Go [here](https://console.developers.google.com) to the Google API console and create a project tied to a Google Account. The name of the project does not matter.
* Click on the "Create" button.
* This should bring you to the dashboard of that project. Click on the "[+]Enable API" button.
* This should bring you to the "Library" tab. This will have a list of all the available Google APIs. We are concerned with the Google Drive API. Under "Google Apps APIs" select "Drive API". This will bring you to the Google Drive API about page.
* Select the "Enable" button towards the top of the screen. A warning box will appear under the button saying the project cannot be used until credentials are established.
* Go to the credentials tab on the left navigation pane. Click on "Create credentials" and select "Help Me Choose".
* Under the first drop down select "Google Drive API".
* Under the second drop down select "Web Server".
* Select the "User Data" radio button.
* Click on "What credentials do I need?". This should put you to the proper credential creation wizard for OAuth.
* Choose a name for the client. Under "Authorized JavaScript origins" put "http://localhost:8080" and under "Authorized Redirect URIs" put "http://localhost:8080/" and then click "Create client ID".
* Fill in the desired email address for the tool and fill in the product name (e.g. "Let It Rain") for the consent screen information.
* Download the credentials (renaming the file from client_id.json to client_secrets.json) and place the credentials file in the same directory as the LetItRain code.
* Now the tool can be used. When running the main script, a link will be presented to the user. Copy and paste that link into a browser window and select "Allow" for the tool to grant access for the API calls.
