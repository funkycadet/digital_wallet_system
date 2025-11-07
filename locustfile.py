# import random
# import uuid
# import json
# from datetime import datetime, timezone
# from locust import HttpUser, task, between
# from faker import Faker
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# fake = Faker()


# locustfile.py (in repo root)
from locust import HttpUser, task, between
import uuid


class WalletUser(HttpUser):
    wait_time = between(0.1, 0.5)
    wallet_id = None

    def on_start(self):
        # Create wallet
        r = self.client.post("/wallets", json={"user_id": "loadtest"})
        self.wallet_id = r.json()["wallet_id"]
        self.wallet_version = 0 # Initial version after creation

        # Get initial wallet state to set the correct version
        r = self.client.get(f"/wallets/{self.wallet_id}")
        if r.status_code == 200:
            self.wallet_version = r.json()["version"]
        else:
            print(f"Failed to get wallet {self.wallet_id} details: {r.text}")


    @task(5)
    def fund(self):
        # Use the current wallet_version for optimistic locking
        r = self.client.post(
            f"/wallets/{self.wallet_id}/fund",
            json={"amount": "10.00", "version": self.wallet_version}
        )
        if r.status_code == 200:
            # Update the wallet_version for subsequent requests
            self.wallet_version = r.json()["version"]
        elif r.status_code == 409:
            # Stale data, retrieve latest version and retry (or handle as appropriate)
            print(f"Stale data for wallet {self.wallet_id}, retrying...")
            r_get = self.client.get(f"/wallets/{self.wallet_id}")
            if r_get.status_code == 200:
                self.wallet_version = r_get.json()["version"]
            else:
                print(f"Failed to get latest wallet version: {r_get.text}")
        else:
            print(f"Fund failed for wallet {self.wallet_id}: {r.text}")

    @task(1)
    def transfer(self):
        other = str(uuid.uuid4())
        self.client.post(
            f"/wallets/{self.wallet_id}/transfer",
            json={"to_wallet_id": other, "amount": "5.00"},
            headers={"X-Version": "0"},
        )
