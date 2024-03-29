import { Injectable } from "@angular/core";
import { AuthorizationService } from "@infrastructure/authorization.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { FeatureFlags } from "./FeatureFlags";
import { BehaviorSubject } from "rxjs";


const TIMEOUT = 5000;

const delay = t => new Promise(resolve => setTimeout(resolve, t));

@Injectable()
export class FeatureFlagService {
    private lastUpdated: Date;
    private featureFlags: FeatureFlags;

    private featureFlagsBehaviorSubject: BehaviorSubject<FeatureFlags> = new BehaviorSubject(
        new FeatureFlags()
    );
    public currentFeatureFlags = this.featureFlagsBehaviorSubject.asObservable();

    constructor(
        private heartstepsServer: HeartstepsServer,
        private authorizationService: AuthorizationService
    ) { }

    private forceRefresh(): Promise<FeatureFlags> {
        this.lastUpdated = new Date();

        return this.authorizationService.isAuthorized()
            .then(() => {
                return this.heartstepsServer.get('feature-flags', undefined, false);
            })
            .then((response) => {
                if (response) {
                    this.featureFlags = response;
                    this.featureFlagsBehaviorSubject.next(response);
                } else {
                    this.featureFlags = new FeatureFlags();
                    this.featureFlagsBehaviorSubject.next(this.featureFlags);
                }
                return this.featureFlags;
            });
    }

    public getFeatureFlags(forceRefresh?: boolean): Promise<FeatureFlags> {
        if (forceRefresh) {
            return this.forceRefresh();
        } else if (this.lastUpdated) {
            if (this.featureFlags == undefined) {
                // just initiated, still fetching initial ff
                return delay(100).then(() => {
                    return this.getFeatureFlags();
                });
            } else {
                // if there is a record of the last update
                let now = new Date();
                if (now.getTime() - this.lastUpdated.getTime() > TIMEOUT) {
                    // if it's been more than 5 seconds since the last update
                    return this.forceRefresh();
                } else {
                    // if it's been less than 5 seconds since the last update
                    return Promise.resolve(this.featureFlags);
                }
            }
        } else {
            // if there is no record of the last update
            return this.forceRefresh();
        }
    }

    public hasFlag(flag: string): Promise<boolean> {
        return this.getFeatureFlags()
            .then((flags) => {
                if (flags) {
                    // this checks if the flags is not: null, undefined, NaN, empty string (""), 0, false
                    let flags_list: string[] = flags.flags.split(", ");
                    return Promise.resolve(flags_list.indexOf(flag) > -1);
                } else {
                    return Promise.resolve(false);
                }
            });
    }

    public getFeatureFlagList(): string[] {
        if (this.featureFlagsBehaviorSubject) {
            if (this.featureFlagsBehaviorSubject.value.flags) {
                // this checks if the flags is not: null, undefined, NaN, empty string (""), 0, false
                let flags: string = this.featureFlagsBehaviorSubject.value.flags;
                let flags_list: string[] = flags.split(", ");
                return flags_list;
            } else {
                return [];
            }
        } else {
            return [];
        }
    }

    public hasFlagNP(flag: string): boolean {
        let flags_list: string[] = this.getFeatureFlagList();
        if (flags_list.indexOf(flag) > -1) {
            return true;
        }
    }



    // // pull feature flags from django
    // public getRecentFeatureFlags(): Promise<FeatureFlags> {
    //     return this.heartstepsServer.get("/feature-flags/", {});
    // }

    // // returns current flags in string form
    // public getFeatureFlagList(): string[] {

    //     // console.log("FF: getFeatureFlags()");
    //     if (this.featureFlags.value.flags) {
    //         // this checks if the flags is not: null, undefined, NaN, empty string (""), 0, false
    //         let flags: string = this.featureFlags.value.flags;
    //         let flags_list: string[] = flags.split(", ");
    //         return flags_list;
    //     }
    //     return [];
    // }

    // // tries to get feature flags from local storage and if fails, pull from django db
    // public get(): Promise<FeatureFlags> {
    //     // console.log("FF: get()");
    //     return this.loadLocalFeatureFlags().catch(() => {
    //         // console.log("FF: catch inside get()");
    //         return this.refreshFeatureFlags();
    //     });
    // }

    // // load feature flags on offline local storage
    // public loadLocalFeatureFlags(): Promise<FeatureFlags> {
    //     // console.log("FF: loadLocalFeatureFlags()");
    //     return this.storage.get(storageKey).then((data) => {
    //         let flags = this.deserializeFeatureFlags(data);
    //         this.featureFlags.next(flags);
    //         return flags;
    //     });
    // }

    // // re-assign local feature flags to flagObject
    // public set(flagObject: FeatureFlags): Promise<FeatureFlags> {
    //     // console.log("FF: set()");
    //     return this.storage
    //         .set(storageKey, this.serialize(flagObject))
    //         .then(() => {
    //             return flagObject;
    //         });
    // }

    // // remove feature flag key and value from local storage
    // public clear(): Promise<boolean> {
    //     // console.log("FF: clear()");
    //     return this.storage.remove(storageKey).then(() => {
    //         return true;
    //     });
    // }

    // public addFeatureFlag(new_flag: string): void {
    //     this.heartstepsServer
    //         .post("/feature-flags/", { add_flag: new_flag })
    //         .catch(() => {
    //             // console.log("error adding feature flags");
    //         })
    //         .then((response) => {
    //             // console.log(response);
    //         });
    // }

    // public removeFeatureFlag(to_remove: string): void {
    //     this.heartstepsServer
    //         .post("/feature-flags/", { remove_flag: to_remove })
    //         .catch(() => {
    //             // console.log("error removing feature flags");
    //         })
    //         .then((response) => {
    //             // console.log(response);
    //         });
    // }

    // // serialize feature flag object into generic dictionary object
    // public serialize(flagObject: FeatureFlags) {
    //     return {
    //         uuid: flagObject.uuid,
    //         flags: flagObject.flags,
    //     };
    // }

    // // explicitly declare FeatureFlags to avoid javascript type errors
    // public deserializeFeatureFlags(data: any): FeatureFlags {
    //     const featureFlags = new FeatureFlags();
    //     featureFlags.uuid = data.uuid;
    //     featureFlags.flags = data.flags;
    //     return featureFlags;
    // }

    // public hasFlag(flag: string): boolean {
    //     let flags_list: string[] = this.getFeatureFlagList();
    //     if (flags_list.indexOf(flag) > -1) {
    //         return true;
    //     }
    //     return false;
    // }

    // public getSubFlagsInNamespace(namespace: string): Array<string> {
    //     let returnArray = new Array<string>();
    //     let namespaceHeading = namespace;

    //     if (!namespaceHeading.endsWith(".")) {
    //         namespaceHeading = namespaceHeading + ".";
    //     }

    //     let flags_list: string[] = this.getFeatureFlagList();
    //     if (flags_list !== []) {
    //         flags_list = flags_list.map(function (x) {
    //             return x.trim();
    //         });

    //         flags_list.forEach((flag) => {
    //             if (flag.startsWith(namespaceHeading)) {
    //                 returnArray.push(flag.substring(namespaceHeading.length));
    //             }
    //         });
    //     }
    //     return returnArray;
    // }

    // // TODO: implement better error checking to throw errors if API fails
    // // refreshes feature flags with django and if fails, load from local storage
    // public refreshFeatureFlags(): Promise<FeatureFlags> {
    //     // console.log("FF: refreshFeatureFlags()");
    //     let localFlags: FeatureFlags;
    //     let areLocalFlags: boolean = false;
    //     // [Junghwan] Reading in local flags asynchronously is dangerous. Because, we are trying to read in from the server, 
    //     // with the sub-logic of local reading result. However, we don't know which one will be returned first. Probably the local one will be
    //     // faster, but we don't know.
    //     // For now, I'll try server-only logic. Later, we should change it into "await" logic.

    //     // this.storage.get(storageKey).then((data) => {
    //     //     localFlags = this.deserializeFeatureFlags(data);
    //     //     areLocalFlags = true;
    //     // });

    //     return this.getRecentFeatureFlags()
    //         .then((data) => {
    //             if (!data.uuid || data.uuid == "") {
    //                 throw "Could not refresh feature flags: invalid UUID";
    //             }
    //             if (areLocalFlags && localFlags.uuid !== data.uuid) {
    //                 throw "Could not refresh feature flags: UUID does not match";
    //             }
    //             // console.log("FF: refreshFeatureFlags promise SUCCESS", data);

    //             let flags = this.deserializeFeatureFlags(data);
    //             this.featureFlags.next(flags);
    //             return this.set(flags);
    //         })
    //         .catch(() => {
    //             // console.log("FF: catch inside refreshFeatureFlags()");
    //             // return this.loadLocalFeatureFlags();
    //             return Promise.reject(undefined);
    //         });
    // }
}
