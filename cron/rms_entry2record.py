print "Running SMS request parse script"

marker  = db(db.gis_marker.name=="phone").select()
feature = db(db.gis_feature_class.name=="SMS").select()

marker_id = marker[0]['id'] if len(marker) == 1 else None
feature_id = feature[0]['id'] if len(feature) == 1 else None

def rss2record(entry):
    myd = {}
    locd = {}

    myd['ush_id'] = entry['id']
    myd['link'] = entry['link']	 # url for the entry
    myd['author'] = entry['author']
    year = entry.updated_parsed[0]
    month = entry.updated_parsed[1]
    day = entry.updated_parsed[2]
    hour = entry.updated_parsed[3]
    minute = entry.updated_parsed[4]
    myd['updated'] = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    myd['title'] = entry['title']
    myd['sms'] = entry['sms']
    myd['smsrec'] = entry['smsrec']
    myd['phone']=entry['phone']
    myd['categorization'] = entry['categorization'] 
    myd['firstname'] = entry['firstname'] 
    myd['lastname'] = entry['lastname']
    myd['status'] = entry['status']
    myd['address'] = entry['address']
    myd['city'] = entry['city']
    myd['department'] = entry['department']
    myd['summary'] = entry['summary']
    myd['notes'] = entry['notes']
    myd['actionable'] = True if entry['actionable'] != '0' else False

    # Fix escape characters: 
    myd["sms"] = " ".join(myd["sms"].split())
    myd["sms"] = myd["sms"].replace('\\"', '"')
    myd["sms"] = myd["sms"].replace("\\'", "'")

    myd["notes"] = " ".join(myd["notes"].split())
    myd["notes"] = myd["notes"].replace('\\"', '"')
    myd["notes"] = myd["notes"].replace("\\'", "'")

    # Add location information. The key name contains a colon, and for
    # this reason, is platform dependent. Thus, we just look for any
    # entry that ends in "point":
    for key in entry.keys():
        if key[-5:] == "point":
            # Found the location info
            gpoint = entry[key].split()
            lat = float(gpoint[0])
            lon = float(gpoint[1])

            # Ushahidi uses a 0,0 lat/lon to indicate no lat lon.
            if abs(lat) > 1.0e-8 and abs(lon) > 1.0e-8:
                locd['lat' ] = lat
                locd['lon' ] = lon
                name = "SMS: "
                if myd['categorization'] != "":
                    name += myd['categorization']
                else: 
                    name += "No category"

                locd['name'] = name

                if marker_id is not None:
                    locd['marker_id'] = marker_id
                if feature_class_id is not None:
                    locd['feature_class_id'] = feature_id


    return myd, locd


def sms_to_metadata(sms_dict):

    metadata = {}
    metadata["event_time" ] = sms_dict["updated"]

    desc = sms_to_description(sms_dict)
    desc = " ".join(desc.split())
    desc = desc.replace('"', '\\"')
    desc = desc.replace("'", "\\'")
    
    metadata["description"] = desc
    metadata["location_id"] = locid

    return metadata

def sms_to_description(sms_dict):

    desc = sms_dict["sms"]

    if sms_dict["notes"] != "":
        if desc == "":
            desc += sms_dict["notes"]
        else:
            desc += " NOTE: " + sms_dict["notes"]

    if sms_dict["categorization"] != "":
        desc = sms_dict["categorization"] + ": " + desc
    
    return desc

def sms_to_request(sms_dict, sms_id):

    d = rms_req_source_type
    request_dict = {}
    request_dict["location_id"] = sms_dict["location_id"]
    request_dict["timestamp"  ] = sms_dict["updated"    ]
    request_dict["message"    ] = sms_to_description(sms_dict)
    request_dict["source_id"  ] = sms_id
    request_dict["source_type"] = d.keys()[d.values().index("SMS")]
    return request_dict

import datetime
import gluon.contrib.feedparser as feedparser
url_base = "http://75.101.195.137/rss.php?key=yqNm7FHSwfdRb8nC2653"

N = 100
start = 0
done = False
while done == False:

    url = url_base + "&limit=" + str(start) + "," + str(N)
    d = feedparser.parse(url)

    for entry in d.entries:
        rec, locd = rss2record(entry)
        # Don't import duplicates
        if db(db.rms_sms_request.ush_id == rec['ush_id']).count() == 0:

            locid = None
            if locd != {}:
                # Calculate WKT for display on Map
                locd['wkt'] = 'POINT(%f %f)' % (locd['lon'], locd['lat'])
                locid = db.gis_location.insert(**locd)

            rec["location_id"] = locid
            smsid = db.rms_sms_request.insert(**rec)

            if locid != None:
                db(db.gis_location.id == locid).update(name="SMS " + repr(smsid))

            # Add media_metadata entry to show additional
            # information on the map
            db.media_metadata.insert(**sms_to_metadata(rec))

            # Insert the request:
            db.rms_req.insert(**sms_to_request(rec, smsid))
        else:
            done = True
            break
        
    start = start + N
    
    if len(d["entries"]) == 0:
        done = True

db.commit()
