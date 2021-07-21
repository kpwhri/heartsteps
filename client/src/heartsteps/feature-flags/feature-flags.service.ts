import { Injectable, OnDestroy } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { BehaviorSubject } from "rxjs";
import { FeatureFlags } from "./FeatureFlags";

@Injectable()
export class FeatureFlagService {
    private featureFlags: BehaviorSubject<FeatureFlags> = new BehaviorSubject(
        new FeatureFlags()
    );
    public currentFeatureFlags = this.featureFlags.asObservable();
    public featureFlagRefreshInterval: any;

    constructor(private heartstepsServer: HeartstepsServer) {
        this.getFeatureFlags();
        // TODO: check to make sure we aren't making too many frequent, unnecessary requestss
        this.featureFlagRefreshInterval = setInterval(() => {
            this.refreshFeatureFlags();
        }, 10000);
    }

    // pull feature flags from django
    public getRecentFeatureFlags(): Promise<FeatureFlags> {
        return this.heartstepsServer.get("/feature-flags/", {});
    }

    // re-initialize this.featureFlags and returns current flags in array
    public getFeatureFlags(): FeatureFlags {
        this.getRecentFeatureFlags().then((data) => {
            let flags = this.deserializeFeatureFlags(data);
            this.featureFlags.next(flags);
        });
        return this.featureFlags.value;
    }

    public addFeatureFlag(new_flag: string): void {
        this.heartstepsServer
            .post("/feature-flags/", { add_flag: new_flag })
            .catch(() => {
                // console.log("error adding feature flags");
            })
            .then((response) => {
                // console.log(response);
            });
    }

    public removeFeatureFlag(to_remove: string): void {
        this.heartstepsServer
            .post("/feature-flags/", { remove_flag: to_remove })
            .catch(() => {
                // console.log("error removing feature flags");
            })
            .then((response) => {
                // console.log(response);
            });
    }

    // explicitly declare FeatureFlags to avoid javascript type errors
    public deserializeFeatureFlags(data: any): FeatureFlags {
        const featureFlags = new FeatureFlags();
        featureFlags.uuid = data.uuid;
        featureFlags.flags = data.flags;
        return featureFlags;
    }

    public hasNotificationCenterFlag(): boolean {
        // TODO: change magic string
        return this.hasFlag("notification_center");
    }

    public hasFlag(flag: string): boolean {
        if (this.featureFlags.value.flags !== "") {
            let flags: string = this.featureFlags.value.flags;
            if (flags.includes(flag)) {
                return true;
            }
        }
        return false;
    }

    public refreshFeatureFlags() {
        this.getFeatureFlags();
    }
}
