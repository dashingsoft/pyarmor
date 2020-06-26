import logging

# {PyArmor Plugins}


def main():
    logging.info("Run plugin: check_multi_mac")
    # PyArmor Plugin: check_multi_mac()

    logging.info("Run plugin: check_ntp_time")
    # PyArmor Plugin: check_ntp_time()

    logging.info("Run plugin: check_docker")
    # PyArmor Plugin: check_docker()

    logging.info("Run plugin: check_multiple_machine")
    # PyArmor Plugin: check_multiple_machine()

    logging.info("All plugins work fine")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
