# Swift addons by SAP

This repo contains some addon middlewares that we use at SAP to support our workflows in
[OpenStack Swift](https://github.com/openstack/swift).

## Installation

```
pip install git+https://github.com/sapcc/swift-sysmeta-domain-override-middleware
```

Then follow the instructions for the specific middlewares as shown below.

## Middlewares

### sysmeta-domain-override

Our Swift is configured for manual account creation such that all accounts are created by an automated process (and
assigned reasonable quotas in the same step). Because the reseller user who performs the account creation resides in a
different domain than customer projects, accounts created by it will not have the correct
`X-Account-Sysmeta-Project-Domain-Id` attribute (which we need for our internal bookkeeping).

This middleware solves this problem by allowing reseller users to specify the domain ID for the project in question
explicitly with the `X-Account-Project-Domain-Id-Override` header.

To enable this middleware, add the following snippet to the `/etc/swift/proxy-server.conf`:

```conf
[filter:sysmeta-domain-override]
use = egg:sapcc-swift-addons#middleware
```

Then, in the same file, add `sysmeta-domain-override` to the application pipeline directly **after** the `keystoneauth` middleware, but also **after** the `gatekeeper` middleware.
