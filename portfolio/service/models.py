import motorengine


class Position(motorengine.Document):
    symbol = motorengine.StringField(max_length=6)
    units = motorengine.IntField(default=0)
    price = motorengine.DecimalField()

    def update(self, units, price):
        if self.units + units < 0:
            raise Exception('Not enough units!')

        if units < 0:
            pnl = units * (price - float(self.price))
            self.units += units
        else:
            pnl = 0
            total_units = self.units + units
            self.price = (self.units * float(self.price) + units * price) / total_units
            self.units = total_units

        return pnl

    def serialize(self):
        return {
            'symbol': self.symbol,
            'units': self.units,
            'price': float(self.price),
        }


class Portfolio(motorengine.Document):
    user = motorengine.IntField(required=True)
    cash = motorengine.IntField(default=1000000)
    positions = motorengine.ListField(motorengine.EmbeddedDocumentField(Position))

    async def make_deal(self, sym, units, price):
        if units == 0:
            raise Exception('Units cannot be zero!')

        amount = units * price
        if amount > self.cash:
            raise Exception('Not enough cash!')

        pnl = 0
        for position in self.positions:
            if position.symbol == sym:
                pnl = position.update(units, price)
                if position.units == 0:
                    self.positions.remove(position)
                break
        else:
            if units < 0:
                raise Exception('Not enough units!')
            else:
                self.positions.append(Position(symbol=sym, units=units, price=price))

        self.cash -= amount
        self.cash += pnl
        await self.save()

    async def reset(self):
         self.cash = 1000000
         self.positions = []
         await self.save()

    def serialize(self):
        return {
            'user': self.user,
            'cash': self.cash,
            'positions': [p.serialize() for p in self.positions],
        }
