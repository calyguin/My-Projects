# My Projects
These are essentially my first projects I made with Python.


## CSV File Filter

There is a set of data on the values of real estate in the UK (it can be found by following the link: https://disk.yandex.ru/d/ZTnv3LiUeqEK5A, description of the columns: https://www.gov.uk/guidance/about-the-price-paid-data).

The script is creating a new .csv file containing all the real estate sold more than once.


## Techsupport Script

This is a script for a techsupport employee based on PostgreSQL.

As you run it, you are able to pick one of the incoming requests and respond to it.

(To be able to work, it requires a proper database with incoming requests).


## Goszakupki Parser

This is a parser of Goszakupki portal.

There are 2 version of it:

Version 1 (V1) is pretty slow but reliable.

Version 2 (V2) is a lot faster but incredibly piled up and absolutely unreadable (that was my first experience with multithreading, cut me some slack please -_-).

## Yandex Maps Parser

This is a parser of Yandex Maps.

Since Yandex Maps API cost about a million rubles a year I've decided to make a parser that doesn't cost a thing.

To bypass using their API I used Selenium to connect to the serivce instead of Requests.

It's also armed with multithreading and works pretty fast.

## Telegram Grabber

A very small and easy grabber for Telegram.

It takes messages from given channels based on target words and resend them to the channel you defined as yours.
