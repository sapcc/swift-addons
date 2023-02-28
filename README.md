# Swift addons by SAP

This repo contains addon middlewares that we use at SAP to support our workflows in
[OpenStack Swift](https://github.com/openstack/swift).

## Installation

```
pip install git+https://github.com/sapcc/swift-addons.git
```

Then follow the instructions for the specific middlewares as shown below.

## Middlewares

### sysmeta-domain-override

Our Swift is configured for manual account creation such that all accounts are created by
an automated process (reseller user). The user that performs this automated account
creation resides in a different domain than the project domain where the accounts are
created. Due to this, the newly created accounts have their
`X-Account-Sysmeta-Project-Domain-Id` attribute set to the domain ID of the reseller user
rather than their actual domains where these accounts exist.

This middleware solves this problem by allowing reseller users to specify the domain ID
for the project in question with the `X-Account-Project-Domain-Id-Override` header.

To enable this middleware, add the following snippet to the `proxy-server.conf` file:

```conf
[filter:sysmeta-domain-override]
use = egg:sapcc-swift-addons#sysmeta_domain_override
```

and then in the same file, add `sysmeta-domain-override` to the application pipeline
**directly after** the `keystoneauth` middleware, but also **after** the `gatekeeper`
middleware. For example:

```conf
pipeline = ... gatekeeper ... keystoneauth sysmeta-domain-override ...
```
