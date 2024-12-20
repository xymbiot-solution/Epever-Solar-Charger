import argparse
import sys
import logging
import time
import serial.tools.list_ports
from epevermodbus.driver import EpeverChargeController

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("mppt_epever_history.log", mode='a')
        ]
    )

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Epever Charge Controller Reader",
        epilog="Example usage: python script.py --comport COM4 --baudrate 115200 --slaveaddress 1"
    )
    parser.add_argument(
        "--comport", 
        required=True, 
        help="COM port to connect to the charge controller (e.g., COM4). This parameter is required."
    )
    parser.add_argument(
        "--baudrate", 
        type=int, 
        default=115200, 
        help="Baudrate for the connection (default: 115200). Specify this parameter if using a custom baudrate."
    )
    parser.add_argument(
        "--slaveaddress", 
        type=int, 
        default=1, 
        help="Slave address of the charge controller (default: 1). Use this to specify a different Modbus slave address."
    )
    return parser.parse_args()

def validate_com_port(com_port):
    ports = [port.device for port in serial.tools.list_ports.comports()]
    if com_port not in ports:
        raise ValueError(f"[INFO] COM port {com_port} is not available. Available ports: {', '.join(ports)}")

def reconnect_and_execute(com_port, baud_rate, slave_address):
    while True:
        validate_com_port(com_port=com_port)
        try:
            logging.info(f"[INFO] Reconnecting to {com_port}...")
            epever = EpeverChargeController(portname=com_port, slaveaddress=slave_address, baudrate=baud_rate)
            call_all_functions(comPort=com_port, baudRate=baud_rate, slaveAddress=slave_address, ctl=epever)
            return
        except Exception as e:
            logging.error(f"[INFO] Failed to read from {com_port}. Error: {e}")
            logging.error(f"[INFO] Retrying connection to {com_port} in 5 seconds...")
            time.sleep(5)

def call_all_functions(comPort, baudRate, slaveAddress, ctl):
    function_calls = [
        ("Solar Voltage", ctl.get_solar_voltage),
        ("Solar Current", ctl.get_solar_current),
        ("Solar Power", ctl.get_solar_power),
        ("Load Voltage", ctl.get_load_voltage),
        ("Load Current", ctl.get_load_current),
        ("Load Power", ctl.get_load_power),
        ("Battery Current", ctl.get_battery_current),
        ("Battery Voltage", ctl.get_battery_voltage),
        ("Battery Power", ctl.get_battery_power),
        ("Battery State of Charge", ctl.get_battery_state_of_charge),
        ("Battery Temperature", ctl.get_battery_temperature),
        ("Remote Battery Temperature", ctl.get_remote_battery_temperature),
        ("Controller Temperature", ctl.get_controller_temperature),
        ("Battery Status", ctl.get_battery_status),
        ("Charging Equipment Status", ctl.get_charging_equipment_status),
        ("Discharging Equipment Status", ctl.get_discharging_equipment_status),
        ("Is Day", ctl.is_day),
        ("Is Night", ctl.is_night),
        ("Is Device Over Temperature", ctl.is_device_over_temperature),
        ("Maximum Battery Voltage Today", ctl.get_maximum_battery_voltage_today),
        ("Minimum Battery Voltage Today", ctl.get_minimum_battery_voltage_today),
        ("Rated Charging Current", ctl.get_rated_charging_current),
        ("Rated Load Current", ctl.get_rated_load_current),
        ("Battery Real Rated Voltage", ctl.get_battery_real_rated_voltage),
        ("Battery Type", ctl.get_battery_type),
        ("Battery Capacity", ctl.get_battery_capacity),
        ("Temperature Compensation Coefficient", ctl.get_temperature_compensation_coefficient),
        ("Battery Voltage Control Registers", ctl.get_battery_voltage_control_registers),
        ("Over Voltage Disconnect Voltage", ctl.get_over_voltage_disconnect_voltage),
        ("Charging Limit Voltage", ctl.get_charging_limit_voltage),
        ("Over Voltage Reconnect Voltage", ctl.get_over_voltage_reconnect_voltage),
        ("Equalize Charging Voltage", ctl.get_equalize_charging_voltage),
        ("Boost Charging Voltage", ctl.get_boost_charging_voltage),
        ("Float Charging Voltage", ctl.get_float_charging_voltage),
        ("Boost Reconnect Charging Voltage", ctl.get_boost_reconnect_charging_voltage),
        ("Low Voltage Reconnect Voltage", ctl.get_low_voltage_reconnect_voltage),
        ("Under Voltage Recover Voltage", ctl.get_under_voltage_recover_voltage),
        ("Under Voltage Warning Voltage", ctl.get_under_voltage_warning_voltage),
        ("Low Voltage Disconnect Voltage", ctl.get_low_voltage_disconnect_voltage),
        ("Discharging Limit Voltage", ctl.get_discharging_limit_voltage),
        ("Battery Rated Voltage", ctl.get_battery_rated_voltage),
        ("Default Load On/Off in Manual Mode", ctl.get_default_load_on_off_in_manual_mode),
        ("Equalize Duration", ctl.get_equalize_duration),
        ("Boost Duration", ctl.get_boost_duration),
        ("Battery Discharge", ctl.get_battery_discharge),
        ("Battery Charge", ctl.get_battery_charge),
        ("Charging Mode", ctl.get_charging_mode),
        ("Total Consumed Energy", ctl.get_total_consumed_energy),
        ("Total Generated Energy", ctl.get_total_generated_energy),
        ("Maximum PV Voltage Today", ctl.get_maximum_pv_voltage_today),
        ("Minimum PV Voltage Today", ctl.get_minimum_pv_voltage_today),
        ("Consumed Energy Today", ctl.get_consumed_energy_today),
        ("Consumed Energy This Month", ctl.get_consumed_energy_this_month),
        ("Consumed Energy This Year", ctl.get_consumed_energy_this_year),
        ("Generated Energy Today", ctl.get_generated_energy_today),
        ("Generated Energy This Month", ctl.get_generated_energy_this_month),
        ("Generated Energy This Year", ctl.get_generated_energy_this_year),
        ("Real Time Clock (RTC)", ctl.get_rtc),
    ]
    
    for description, func in function_calls:
        success = False
        while not success:
            if func:
                try:
                    result = func()
                    logging.info(f"{description}: {result}")
                    success = True
                except Exception as e:
                    logging.error(f"[INFO] Error calling {description}: {e}")
                    reconnect_and_execute(com_port=comPort, baud_rate=baudRate, slave_address=slaveAddress)
            else:
                logging.info(f"[INFO] Function {description} is not available.")

def main():
    args = parse_arguments()
    setup_logging()
    reconnect_and_execute(com_port=args.comport, baud_rate=args.baudrate, slave_address=args.slaveaddress)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("[EXIT] Program terminated by user.")
        sys.exit(0)