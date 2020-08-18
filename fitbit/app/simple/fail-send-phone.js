import * as fs from "fs";

const PHONE_ERROR_FILE = "phone_error.json";
const PHONE_FILE_NOT_FOUND = `Error: Couldn't find file: ${PHONE_ERROR_FILE}`;

class PhoneErrorCounter {
    // Time stored as milliseconds since 1970.01.01 for easy maths
    constructor(time) {
        this.currentTime = new Date().getTime();
        this.errorTime = time;
    }
  
    deleteFile() {
        try {
        fs.unlinkSync(PHONE_ERROR_FILE);
    } catch (err) {
      }
    }
  
    // Get data from file system and convert to JSON array
    getData() {
      let errData;
      try {
        errData = fs.readFileSync(PHONE_ERROR_FILE, "json");
    } catch (err) {
        // Fitbit's JS engine doesn't return err.code
        // but the following text is used.
        if(err == PHONE_FILE_NOT_FOUND) {
            errData = '[{"time": 0}]';
        } else {
            throw err;
        }
      }
      return JSON.parse(errData);
    }
    
    // Drop array members with datetimes before 48 hrs ago
    filterByTime(errData) {
        let filtered = [];
        for (let reading of errData) {
            if (reading.time === '0') {
                continue;
            }

            var diff = this.currentTime - reading.time;
            var total_seconds = Math.floor(diff / 1000);
            var total_minutes = Math.floor(total_seconds / 60);
            var total_hours = Math.floor(total_minutes / 60);

            if (total_hours <= 48) {
                filtered.push(reading);
            }
        }
        return filtered;
    }
    
    // Append new reading and drop older data
    updateData(errData) {
        errData.push({"time": this.errorTime});
        
        // cut off errors not in last 48 hours
        let selectData = this.filterByTime(errData);
        return selectData;
    }
    
    calculateTotalErrors(errData) {
        let n = 0;
        for (let reading of errData) {
            n += 1;
        }
        return n;
    }
    
    // Save the new step count array
    saveFile(errData) {
        fs.writeFileSync(PHONE_ERROR_FILE, JSON.stringify(errData), "json");
    }
}

export function initialize(callback) {
    callback({numErr: 0});
}

export function update(time, callback) {
    let pe = new PhoneErrorCounter(time);
    let oldpeData = pe.getData();
    let newpeData = pe.updateData(oldpeData);
    pe.saveFile(newpeData);
    let totNumErr = pe.calculateTotalErrors(newpeData);
    callback({numErr: totNumErr});
}

export function refresh(callback) {
    let pe = new PhoneErrorCounter(null);
    let oldpeData = pe.getData();
    let filterpeData = pe.filterByTime(oldpeData);
    pe.saveFile(filterpeData);
    let totNumErr = pe.calculateTotalErrors(filterpeData);
    callback({numErr: totNumErr});
}
  