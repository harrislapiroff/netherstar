Nether Star
===========

A web-based dashboard that spins up Digital Ocean droplets for Minecraft Servers.

🚨 In development and barely functional

Development
-----------

To run the development server locally:

First, get a [DigitalOcean API Token][token] for your DigitalOcean account

Then:

```bash
# You only need to create the .env file once
echo "DIGITALOCEAN_TOKEN=<YOUR_TOKEN_HERE>" > .env

# Run this every time you want to start the dashboard
docker-compose up

# To seed the database with Minecraft and forge versions, run the
docker-compose run django ./manage.py update_minecraft_versions
docker-compose run django ./manage.py update_forge_versions
```

⚠️ **This will use your DigitalOcean account to create Droplets with Minecraft
servers when you create them in the dashboard!**
You will be charged for these Droplets if you leave them on.
Be sure to check your DO account when you are done developing and clean up any
Droplets and Volumes you don't want to keep.

[token]: https://cloud.digitalocean.com/settings/applications
