import numpy as np
import math
import random



class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated, standard_cars, rescue_cars, buses, trucks, standard_cars_p, rescue_cars_p, buses_p, trucks_p):
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
        self._standard_cars = standard_cars
        self._rescue_cars = rescue_cars
        self._buses = buses
        self._trucks = trucks
        self._standard_cars_p = standard_cars_p
        self._rescue_cars_p = rescue_cars_p
        self._buses_p = buses_p
        self._trucks_p = trucks_p

    def generate_routefile(self, seed):
        """
        Generation of the route of every car for one episode
        """
        np.random.seed(seed)  # make tests reproducible

        # the generation of cars is distributed according to a weibull distribution
        timings = np.random.weibull(2, self._n_cars_generated)
        timings = np.sort(timings)

        # reshape the distribution to fit the interval 0:max_steps
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = self._max_steps
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)  # round every value to int -> effective steps when a car will be generated

        # produce the file for cars generation, one car per line
        with open("intersection/episode_routes.rou.xml", "w") as routes:
            print("""<routes>

            <vType accel="1.0" decel="4.5" id="standard_car" length="5.0" minGap="2.5" maxSpeed="25" sigma="0.5" />
            <vType accel="1.0" decel="4.5" id="bus" length="5.0" minGap="2.5" maxSpeed="25" sigma="0.5" guiShape="bus/coach" />
            <vType vClass="truck" accel="1.0" decel="4.5" id="truck" length="5.0" minGap="2.5" maxSpeed="25" sigma="0.5" guiShape="truck" />
            <vType vClass="emergency" id="rescue" guiShape="emergency" >
              <param key="has.bluelight.device" value="true"/>
            </vType>
         <!--            <type id="truck" priority="3" numLanes="3" speed="38.89">-->
<!--               <restriction vClass="truck" speed="27.89"/>-->
<!--            </type>-->
<!--            <vType id="rescue" vClass="emergency" speedFactor="1.5">-->
<!--               <param key="has.bluelight.device" value="true"/>-->
<!--            </vType>-->

            <route id="W_N" edges="W2TL TL2N"/>
            <route id="W_E" edges="W2TL TL2E"/>
            <route id="N_E" edges="N2TLT TL2E"/>
            <route id="N_S" edges="N2TL TL2S"/>
            <route id="E_W" edges="E2TL TL2W"/>
            <route id="E_S" edges="E2TL TL2S"/>
            <route id="S_W" edges="S2TLT TL2W"/>
            <route id="S_N" edges="S2TL TL2N"/>""", file=routes)

            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()
                if straight_or_turn < 0.75:  # choose direction: straight or turn - 75% of times the car goes straight
                    route_straight = np.random.randint(1, 5)  # choose a random source & destination
                    if route_straight == 1:
                        print('    <vehicle id="W_E_%i" type="%s" route="W_E" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, self.select_car_type(), step), file=routes)
                    elif route_straight == 2:
                        print('    <vehicle id="E_W_%i" type="%s" route="E_W" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, self.select_car_type(), step), file=routes)
                    elif route_straight == 3:
                        print('    <vehicle id="N_S_%i" type="%s" route="N_S" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, self.select_car_type(), step), file=routes)
                    else:
                        print('    <vehicle id="S_N_%i" type="%s" route="S_N" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, self.select_car_type(), step), file=routes)
                else:  # car that turn -25% of the time the car turns
                    route_turn = np.random.randint(1, 4)  # choose random source source & destination
                    if route_turn == 1:
                        print('    <vehicle id="W_N_%i" type="standard_car" route="W_N" depart="%s" departLane="random" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 2:
                        print('    <vehicle id="N_E_%i" type="standard_car" route="N_E" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 3:
                        print('    <vehicle id="E_S_%i" type="standard_car" route="E_S" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 4:
                        print('    <vehicle id="S_W_%i" type="standard_car" route="S_W" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)


            print("</routes>", file=routes)

    def select_car_type(self):
        car_types = []
        car_probabilities = []
        if self._standard_cars:
            car_types.append('standard_car')
            car_probabilities.append(self._standard_cars_p)
        if self._buses:
            car_types.append('bus')
            car_probabilities.append(self._buses_p)
        if self._trucks:
            car_types.append('truck')
            car_probabilities.append(self._trucks_p)
        if self._rescue_cars:
            car_types.append('rescue')
            car_probabilities.append(self._rescue_cars_p)

        if len(car_types) < 1 or len(car_probabilities):
            car_types = ['standard_car', 'bus', 'truck', 'rescue']
            car_probabilities = [0.7, 0.15, 0.10, 0.05]

        selected_type = random.choices(car_types, car_probabilities)[0]
        return selected_type