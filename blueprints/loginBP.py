from flask import Blueprint, request

borderBP = Blueprint("borderBP", __name__)

@borderBP.route('/checkingborders', methods=['GET', 'POST'])
def mainStatus() -> str:
    if request.method == 'GET':
        return "Up and Running!"