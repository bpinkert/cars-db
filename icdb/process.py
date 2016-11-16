"""
        ____
   ____/ / /_
  / __  / __/
 / /_/ / /_
 \__,_/\__/     dealertrack technologies

Welcome to the Internet Car Database v{}
"""
import argparse
import logging

from . import __version__
from .db import db_cursor

# Setup logging
logger = logging.getLogger(__name__)
FORMAT = "%(asctime)-15s %(name)s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.ERROR)


def get_input(question):
    return raw_input(question)

def _get_year(year=None):
    """ Keep asking the user for a year until it is finally valid.
    """
    if year:
        if year.isdigit():
            if len(year) == 4:
                return year

    year = get_input("{:>25}".format("Enter car year [2013]: "))
    return _get_year(year)


def create_car():
    """ Let the user input parameters to create a new car, and
    insert it to the database.
    """
    with db_cursor() as db:
        num = get_input("{:>23}".format("Enter reference number [1-20]: "))
        year = _get_year()
        make = get_input("{:>24}".format("Enter car make [Toyota]: "))
        model = get_input("{:>25}".format("Enter car model [Camry]: "))

        row = (num, year, make, model)

        if not all(row):
            logger.error("One or more of your answers were empty, please try again.")
            return

        print "Inserting a {} {} {} to the database...".format(year, make, model)
        db.execute("INSERT INTO cars VALUES (?, ?, ?, ?)", row)


def import_cars(csv_file):
    with db_cursor() as db:
        # csv_file = get_input("Input path of CSV file to import into database: ")
        fh = open(csv_file)
        fr = fh.read()
        fs = fr.split()
        for item in fs:
            item.split('\n')
            num = 0
            year = item.split(',')[0]
            make = item.split(',')[1]
            model = item.split(',')[2]

            row = (num, year, make, model)

            # if not all(row):
            #     logger.error("Check your csv file, some fields are missing.")
            #     return

            print "Inserting a {} {} {} into the database...".format(year,make,model)
            db.execute("INSERT INTO cars VALUES (?, ?, ?, ?)", row)
            num = num + 1


def update_car():
    with db_cursor() as db:
        upcar = get_input("Select reference number to update:   ")

        if len(upcar) == 0:
            logger.error("You must select a reference number to update")
            return

        print "Deleting car with reference number {}".format(upcar)
        db.execute("DELETE FROM cars where num=?", (upcar,))
        print "Enter updated car information:\n"
        num = upcar
        year = _get_year()
        make = get_input("{:>24}".format("Enter car make [Toyota]: "))
        model = get_input("{:>25}".format("Enter car model [Camry]: "))

        row = (num, year, make, model)

        if not all(row):
            logger.error("One or more of your answers were empty, please try again.")
            return

        print "Updating car number {} in the database\nwith new information: {} {} {}".format(num, year, make, model)
        db.execute("INSERT INTO cars VALUES (?, ?, ?, ?)", row)


def delete_car():
    # logger.error("This has not been implemented yet.")
    with db_cursor() as db:
        delnum = raw_input("Select reference number to delete:\n")

        if len(delnum) == 0:
            logger.error("You must select a reference number to delete")
            return

        print "Deleting car with reference number {}".format(delnum)
        db.execute("DELETE FROM cars WHERE num=?", (delnum,)) 

def list_cars():
    """ List all cars in the database.
    """
    with db_cursor() as db:
        LAYOUT = "{:<4} {:<4} {:20} {:20}"
        print LAYOUT.format("Num", "Year", "Make", "Model")
        print LAYOUT.format("-" * 4, "-" * 4, "-" * 20, "-" * 20)
        for row in db.execute("SELECT * FROM cars"):
            print LAYOUT.format(*row)


def main():
    parser = argparse.ArgumentParser(description=__doc__.format(__version__),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='be verbose')

    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('-i', '--importcsv',
                         action='store',
                         help='import a CSV file, overwriting the database')
    actions.add_argument('-a', '--add',
                         action='store_true',
                         help='add a car to the database')
    actions.add_argument('-u', '--update',
                         action='store_true',
                         help='update a car in the database')
    actions.add_argument('-d', '--delete',
                         action='store_true',
                         help='delete a car from the database')
    actions.add_argument('-l', '--listcars',
                         action='store_true',
                         help='list the cars in the database')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.importcsv:
        logger.info("importing csv")
        import_cars(args.importcsv)

    if args.add:
        logger.info("adding new car")
        create_car()

    if args.update:
        logger.info("updating a car")
        update_car()

    if args.delete:
        logger.info("deleting a car")
        delete_car()

    if args.listcars:
        logger.info("listing cars")
        list_cars()
