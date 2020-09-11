#Shop Reservation
Version 1.0 11-09-2020

* A web application that allows a customer to book a reservation to a shop near his pincode.
* The portal also allows a seller / shopkeeper to register his shop on the portal, he can then see his shop reservations on the portal.
* The portal allows a user to search the shops via PIN Code / Postal Code such that he is able to see only the closest shops near his house.
* The portal only allows one shop to be registered per login account.

-------------------------------------------------------------------------

1. This is a flask web application written in python.
2. A sqlite databse is used with various tables in order to ensure proper and optimized funtionality of the webapplication.
3. The web application automatically clears the table of data after 3 days since there is no use of the data once used and thus is not required.
4. The web application also uses the CS50 library thus installing that is required to run the application outside the CS50 IDE
------------------------------------------------------------------------

To run the application with CS50 library already installed:

``` Python
 cd finalprojekt
 flask run
 ```