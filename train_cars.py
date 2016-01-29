#
#Master data of train cars
#

class RailroadCar():
    '''
    Master data for each train car
    Not mandatory unless asset management is required
    '''
    def __init__(self, carid, length=20.0):
        self.carid = carid
        self.length = length
        # more attribute should be added in reality

class CarUnit():
    '''
    Master data for car unit
    Car Unit stands for smallest unit to operate train
    '''
    def __init__(self, unitid, cars=0, assigned_cars=[], max_speed=100, acceleration=3.0, deceleration=3.0, emergency_factor=1.5):
        self.unitid = unitid
        self.assigned_cars = assigned_cars
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.emergency_factor = emergency_factor
        self.cars = cars

        if self.cars == 0:
            self.cars = 3   #in case neither cars nor assigned_cars provided
            self.length = 60.0
        else:
            self.cars = cars
            self.length = cars * 20.0
        if self.assigned_cars:
            self.cars = len(self.assigned_cars)
            self.length = 0.0
            for car in self.assigned_cars:
                self.length += car.length
        # more attributes to be added

class UnitSet():
    '''
    Unit set to be assigned to Train(number)
    '''
    def __init__(self, unitsetid, location, cars=0, assigned_unit=['DUMMY'], max_speed=100.0):
        self.unitsetid = unitsetid
        self.location = location
        self.assigned_unit = assigned_unit
        if assigned_unit == ['DUMMY']:
            self.assigned_unit = []
            #Assign dummy CarUnit
            if max_speed >= 140.0:
                acceleration=2.5
                deceleration=2.5
                emergency_factor = 1.8
                self.assigned_unit.append(CarUnit(unitid='DUMMY', cars=cars, max_speed=max_speed,
                                                  acceleration=acceleration, deceleration=deceleration,
                                                  emergency_factor=emergency_factor))
            else:
                self.assigned_unit.append(CarUnit(unitid='DUMMY', cars=cars, max_speed=max_speed))
        self.max_speed = None
        self.acceleration = None
        self.deceleration = None
        self.emergency_factor = None
        self.length = 0.0
        self.cars = 0
        for unit in self.assigned_unit:
            # attribute should be equal to lowest ones
            if not self.max_speed or self.max_speed > unit.max_speed:
                self.max_speed = unit.max_speed
            if not self.acceleration or self.acceleration > unit.acceleration:
                self.acceleration = unit.acceleration
            if not self.deceleration or self.deceleration > unit.decceleration:
                self.deceleration = unit.deceleration
            if not self.emergency_factor or self.emergency_factor > unit.emergency_factor:
                self.emergency_factor = unit.emergency_factor
            # simply add values
            self.cars += unit.cars
            self.length += unit.length
        self.head_offset = round(self.length / 2 / 1000, 3)
        self.tail_offset = round(self.length / 2 / 1000, 3) * -1
        self.booked = None  #train_number to be assigned

if __name__ == '__main__':
    #unit test: create 20 unitsets
    unitsets = []
    for i in range(1,21):
        unitsets.append(UnitSet(unitsetid=i, cars=3, max_speed=100.0))
    for i in range(51,56):
        unitsets.append(UnitSet(unitsetid=i, cars=6, max_speed=160.0))
    for unitset in unitsets:
        print(unitset.unitsetid, unitset.cars, unitset.length, unitset.max_speed,
              unitset.head_offset, unitset.tail_offset, unitset.acceleration, unitset.deceleration,
              unitset.emergency_factor, unitset.assigned_unit)