import * as fs from "fs";

const WATCH_ERROR_FILE = "watch_error.json";
const WE_FILE_NOT_FOUND = `Error: Couldn't find file: ${WATCH_ERROR_FILE}`;

class WatchErrorCounter {
    // Time stored as milliseconds since 1970.01.01 for easy maths
    constructor() {
        this.currentTime = new Date().getTime();
    }
  
    deleteFile() {
        try {
        fs.unlinkSync(WATCH_ERROR_FILE);
    } catch (err) {
      }
    }
  
    // Get data from file system and convert to JSON array
    getData() {
      let errData;
      try {
        errData = fs.readFileSync(WATCH_ERROR_FILE, "json");
    } catch (err) {
        // Fitbit's JS engine doesn't return err.code
        // but the following text is used.
        if(err == WE_FILE_NOT_FOUND) {
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
        errData.push({"time": this.currentTime});
        
        // cut of errors not in last 48 hours
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
        fs.writeFileSync(WATCH_ERROR_FILE, JSON.stringify(errData), "json");
    }
}

export function initialize(callback) {
    callback({numErr: 0});
}

export function update(callback) {
    let we = new WatchErrorCounter();
    let oldweData = we.getData();
    let newweData = we.updateData(oldweData);
    we.saveFile(newweData);
    let totNumErr = we.calculateTotalErrors(newweData);
    callback({numErr: totNumErr});
}
  
export function refresh(callback) {
    let we = new WatchErrorCounter();
    let oldweData = we.getData();
    let filterweData = we.filterByTime(oldweData);
    we.saveFile(filterweData);
    let totNumErr = we.calculateTotalErrors(filterweData);
    callback({numErr: totNumErr});
}
  