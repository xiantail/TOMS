class RailroadCar():
    def __init__(self, carid, length=20.0):
        self.carid = carid
        self.length = length
        # more attribute should be added in reality

class CarSet():
    def __init__(self, carsetid, cars, max_speed=100, acc=3.0, dec=3.0):
        self.carsetid = carsetid
        self.length = 0
        self.acc = acc
        self.dec = dec
        self.headoffset = 0.0
        self.tailoffset = 0.0
        self.cars = cars
        if cars:
            for car in cars:
                self.length += car.length
        else:   #should not happen, only for simulation purpose
            self.length = 80.0
        self.headoffset = round(self.length / 2 / 1000, 3)
        self.tailoffset = round(self.length / 2 / 1000 * -1, 3)


if __name__ == '__main__':
    # Unit test : Generate 20 CarSets with 4 cars
    prefix = 'T'
    carnum = 20000
    carlist = []
    for i in range(1,81):
        car = RailroadCar(prefix + str(carnum + i), 20.0)
        carlist.append(car)
    print(len(carlist))

    set_prefix = 'TS'
    setnum = 10
    carsetlist = []
    for i in range(20):
        assigned_cars = (carlist[i*4:i*4+4])
        carset = CarSet(set_prefix + str(setnum + i), assigned_cars, 100.0, 3.0, 3.0)
        carsetlist.append(carset)
    print(len(carsetlist))

    for carset in carsetlist:
        print(carset.carsetid, carset.length, carset.cars[0].carid)
