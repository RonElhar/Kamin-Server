# Kamin-Server

Kamin-Server is a Python code repository of a deployed web app, for conducting experiments of non-convergent discussions, with integration ready advanced visualizations

It contains an API for transfering data to Kamin-Client, and managing the application data.

## Getting Started

* Make sure you have Python 3.7 installed on your computer

* After cloning the repositoy to your preffered code editor, open the terminal and do the following:
  * Create virtualenv & activate it
  * cd to the directory where requirements.txt is located
  * Run in your shell:
    ```bash
    pip install -r requirements.txt
    ```
* Create your own MongoDB database.
  * Find instructions at https://www.mongodb.com/
* In the root directory of the project create file db_config.py and write your credentials to config str variable, for example:
      ```bash
      config = "mongodb+srv://bkla_admin:dasfdsafsafsda@cluster0-erofa.mongodb.net/test?retryWrites=true&w=majority"
      ```
* Then to start the server run in your shell:
    ```bash
    python kamin_API.py
    ```
And kamin server will run at http://localhost:5000/

Start Kamin-Client to see the interface being used to show the data, instructions at https://github.com/RonElhar/Kamin-Client see README


## To Use Deployment Version of the project

Visit us at http://conversaction.tk:3000/ in order to use the deployed web app
