# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import request
from werkzeug.exceptions import BadRequest
from server import app

class OrderService:
    def __init__(self):
        self.orders = {}
        self.current_id = 0

    def order_index(self):
        app.logger.info('Retrieved all orders')
        return list(self.orders.values())

    def order_index_by_username(self, username):
        try:
            orders = [order for order in self.orders.values() if order["username"] == username]
            app.logger.info(f'Retrieved all orders for user {username}')
            return orders
        except KeyError:
            app.logger.warning(f'Attempt to get non-existent orders for user {username}')
            raise

    def order_show_by_id(self, orderid):
        try:
            order = self.orders[orderid]
            app.logger.info(f'Retrieved order with id {orderid}')
            return order
        except KeyError:
            app.logger.warning(f'Attempt to get non-existent order with id {orderid}')
            raise

    def create_order(self):
        try:
            order = request.get_json()
            self.current_id += 1
            order["id"] = str(self.current_id)
            self.orders[order["id"]] = order
            app.logger.info(f'Created order with id {self.current_id}')
            return order
        except BadRequest as e:
            app.logger.error(f'Error creating order: {str(e)}')
            raise

    def update_order(self, order_id):
        try:
            order_update = request.get_json(force=True)
            order_id_str = str(order_id)
            if order_id_str in self.orders:
                order_update["id"] = order_id_str
                self.orders[order_id_str] = order_update
                app.logger.info(f'Updated order with id {order_id}')
                return order_update
            else:
                app.logger.warning(f'Attempt to update non-existent order with id {order_id}')
                raise KeyError('Order not found')
        except BadRequest as e:
            app.logger.error(f'Error updating order: {str(e)}')
            raise