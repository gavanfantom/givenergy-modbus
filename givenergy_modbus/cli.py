"""Console script for givenergy_modbus."""

import logging

import click

from .client import GivEnergyClient
from .pdu import ReadHoldingRegistersRequest, ReadInputRegistersRequest
from .util import InterceptHandler

_logger = logging.getLogger(__package__)


@click.command()
def main():
    """Main entrypoint for the CLI."""
    # Install our improved logging handler.
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    click.echo("givenergy-modbus")
    click.echo("=" * len("givenergy-modbus"))
    click.echo(
        "A python library to access GivEnergy inverters via Modbus TCP, with no dependency on the GivEnergy Cloud."
    )

    with GivEnergyClient(host="192.168.0.241") as client:
        # _logger.info(f"client {client}: {vars(client)}")
        # _logger.info(f"framer {client.framer}: {vars(client.framer)}")

        request = ReadInputRegistersRequest(base_register=0x0, register_count=60)
        _logger.info(f"request: {request}")
        result = client.execute(request)
        _logger.info(f"result: {result}")

        request = ReadHoldingRegistersRequest(base_register=0x0, register_count=60)
        _logger.info(f"request: {request}")
        result = client.execute(request)
        _logger.info(f"result: {result}")


if __name__ == "__main__":
    main()  # pragma: no cover
