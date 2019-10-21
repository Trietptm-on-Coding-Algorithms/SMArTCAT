import casmMemory as casm
model = "memory model.log"

def mergeFormats():
    formats = iter(casm.allInstructions)
    format = formats.next()
    
    formatting = iter(casm.Formatted(format))
    formatted = formatting.next()[0]
    
    formatMeasurements = {}
    formatMeasurements[format] = []
    count = 0
    stop = False
    with open(model, 'r') as log:
        for line in log:
            if not formatted in line:
                formatted = None
                for format_ in iter(casm.allInstructions):
                    for search in casm.Formatted(format_):
                        if ("%s;" % search[0]) in line:
                            formatted = search[0]
                            format = format_
                if formatted == None:
                    formatted = "Unmatched"
                if format not in formatMeasurements:
                    formatMeasurements[format] = []
            measurements = line.split("  --  ")[1].split(", ")
            if "::" in line:
                writeback = float(line.split("::")[1].replace(" ",""))
            else:
                writeback = None
            if "cc TRUE" in line:
                cc = "cc TRUE"
            elif "cc FALSE" in line:
                cc = "cc FALSE"
            else:
                cc = "no cc"
                
                
            issue = float(measurements[0])
            latency = float(measurements[1][:-1])
            entry = (issue, latency, writeback, cc)
            if entry not in formatMeasurements[format]:
                formatMeasurements[format].append(entry)
            count += 1
            if count % 500 == 0:
                print count
    print "done"
                
    return formatMeasurements
    
def noR1orR2():
    linesNoR1=[]
    linesNoR2=[]
    with open(model, 'r') as log:
        for line in log:
            if "r1" not in line or "r2" not in line:
                print line.split("  --  ")[0:2]
            if "r1" not in line:
                linesNoR1.append(line.split("  --  ")[0:2])
            if "r2" not in line:
                linesNoR2.append(line.split("  --  ")[0:2])
    return (linesNoR1, linesNoR2)
    
def lineToFormat():
    #make sure this function is somewhat efficient
    return 0
    
def earlyBail():
    import re
    earlyBailInsns = {}
    with open(model, 'r') as log:
        for line in log:
            if "cc TRUE" in line:
                line1 = line
            if "cc FALSE" in line:
                line2 = line
                measurements1 = line1.split("  --  ")[1].split(", ")
                iss1 = float(measurements1[0])
                lat1 = float(measurements1[1][:-1])
                measurements2 = line2.split("  --  ")[1].split(", ")
                iss2 = float(measurements2[0])
                lat2 = float(measurements2[1][:-1])
                if (iss1 != -1 and iss2 != -1 and iss1 != iss2) or (lat1 != -1 and lat2 != -1 and lat1 != lat2):
                    key = re.sub("[a-z][a-z] "," ",line1.split("  --  ")[0])
                    if key not in earlyBailInsns:
                        earlyBailInsns[key] = set([])
                    earlyBailInsns[key].add(((iss1, iss2), (lat1, lat2)))
    return earlyBailInsns
    
def roundDown(modelDict):
    """
    rounds all timings towards 0 and removes all failed measurements.
    uses output from mergeFormats as input
    """
    newDict = {}
    for format in modelDict:
        newDict[format] = set()
        for entry in modelDict[format]:
            if int(entry[0]) != -1 and int(entry[1]) != -1:
                if type(entry[2]) == float:
                    writeback = int(entry[2])
                else:
                    writeback = None
                newEntry = (int(entry[0]), int(entry[1]), writeback, entry[3])
                newDict[format].add(newEntry)
    return newDict
    