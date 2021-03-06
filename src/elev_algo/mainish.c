#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "con_load.h"
#include "driver/elevator_hardware.h"
#include "elevator_io_device.h"
#include "fsm.h"
#include "timer.h"

void mainish(int portOffset, void* new_order(int, int), void* finished_order(int)){
    elevator_hardware_init(portOffset);
    printf("C elevator started\n");

    int inputPollRate_ms = 25;
    con_load("elevator.con",
        con_val("inputPollRate_ms", &inputPollRate_ms, "%d")
    )

    ElevInputDevice input = elevio_getInputDevice();

    if(input.floorSensor() == -1){
        fsm_onInitBetweenFloors();
    }

    while(1){
        { // Request button
            static int prev[N_FLOORS][N_BUTTONS];
            for(int f = 0; f < N_FLOORS; f++){
                for(int b = 0; b < N_BUTTONS; b++){
                    int v = input.requestButton(f, b);
                    if(v  &&  v != prev[f][b]){
                        //fsm_onRequestButtonPress(f, b);
                        new_order(f, b);
                    }
                    prev[f][b] = v;
                }
            }
        }

        { // Floor sensor
            static int prev;
            int f = input.floorSensor();
            if(f != -1  &&  f != prev){
                fsm_onFloorArrival(f, finished_order);
            } else if (f != -1 && f == prev && fsm_check_finished_order_at_idle_flag()) {
                finished_order(f);
                fsm_clear_finished_order_at_idle_flag();
            }
            prev = f;
        }


        { // Timer
            if(timer_timedOut()){
                fsm_onDoorTimeout();
                timer_stop();
            }
        }

        usleep(inputPollRate_ms*1000);
    }
}
