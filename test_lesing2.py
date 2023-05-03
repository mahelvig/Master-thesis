from viresclient import SwarmRequest

# Set up connection with server
request = SwarmRequest()
print(request)
# Set collection to use
# - See https://viresclient.readthedocs.io/en/latest/available_parameters.html
request.set_collection("SW_OPER_MAGA_LR_1B")
# Set mix of products to fetch:
#  measurements (variables from the given collection)
#  models (magnetic model predictions at spacecraft sampling points)
#  auxiliaries (variables available with any collection)
# Optionally set a sampling rate different from the original data
request.set_products(
    measurements=["F", "B_NEC"],
    models=["CHAOS-Core"],
    auxiliaries=["QDLat", "QDLon"],
    sampling_step="PT10S"
)
# Fetch data from a given time interval
# - Specify times as ISO-8601 strings or Python datetime
data = request.get_between(
    start_time="2014-01-01T00:00",
    end_time="2014-01-01T01:00"
)
# Load the data as an xarray.Dataset
ds = data.as_xarray()
print(ds)