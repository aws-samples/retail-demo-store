# User Data Generator

generate_users_json.py generates a set of users for the Retail Demo Store.

These user profiles are used in the following ways:

* The Users service provides login services to the user profiles that this crates for the Retail Demo Store
* Workshops which need to generate simulated user behavior data can use the datagenerator library to create simulated events for these user profiles after they are created.  This provides realistic and consistent data across all integrated tools in the Retail Demo Store.

## datagenerator Library

The datagenerator library is a Python library that provides the follwing functions:

* A pool of randomly generated users (see ./datagenerator/users.py)
* The ability to specify a set of user behavior funnels and to then generate events that can be sent to Amazon Personalize, Segment, or Amplitude.  (see ./datagenerator/file.py, amplitude.py, and segment.py)

For examples of usage of the event generator features, see ../workshop/3-Experimentation/3.5-Amplitude-Performance-Metrics.ipynb)
