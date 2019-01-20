# Item Catalog 
this app is project for udacity Fullstack web delveloper 
## About
this project is about city Area as catalog and its neighborhood as items i used flask, oauth2 with google+ and created the database with sqlalchemy

the main python file is `application.py`, SQL database module `cityDB.py` creates the database and tests data using `lotsofArea.py`.
HTML & bootstrap is used for frent end

required librayries is stored in `requirment.txt` file

## instalations

fork or dawnload [FNSD](https://www.google.com/url?q=http://github.com/udacity/fullstack-nanodegree-vm&sa=D&ust=1547877339505000)
download [vagratn](https://www.google.com/url?q=http://vagrantup.com/&sa=D&ust=1547877339504000) , [virtual box](https://www.google.com/url?q=https://www.virtualbox.org/&sa=D&ust=1547877339504000) follow this [link](https://www.google.com/url?q=https://www.udacity.com/wiki/ud088/vagrant&sa=D&ust=1547877339505000) for more instruction

## google login

>Go to Google Dev Console
>Sign up or Login if prompted
>Go to Credentials
>Select Create Crendentials > OAuth Client ID
>Select Web application
>Enter name 'Item Catalog'
>Authorize javascript orign=[http://localhost:5000](http://localhost:5000), redirect URIs =[http://localhost:5000](http://localhost:5000) 
>download json
>rename it to `client_secret.json` and place it in same directory


## json Endpionts

catalog : `/json`

catagories: `/catalog/json`

items: `/item/json`.

