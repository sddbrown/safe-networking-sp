from autofocus import AFSample, AFSampleAbsent


def getDomainAF(domain, apiKey)
# Searching for a single domain #

try:

    # sample is instance of AFSample()
    sample = AFSample.search(domain)

    # Using instrospection, you can analyze the attributes of the AFSample instance
    print "Pulled sample {} and got the follow attributes".format(domain)
    for k,v in sample.__dict__.items():
        print "\t{}={}".format(k, v)

except AFSampleAbsent:
    pass # The sample isn't in AutoFocus
