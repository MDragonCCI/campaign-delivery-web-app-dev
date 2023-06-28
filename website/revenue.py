from flask import Blueprint


revenue = Blueprint('revenue', __name__)


@revenue.route('/revenue')
def revenue_func():
	return "<p>Test</p<"