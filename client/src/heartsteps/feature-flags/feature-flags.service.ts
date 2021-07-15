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
            // console.log("Feature Flags: ", flags);
            this.featureFlags.next(flags);
        });
        return this.featureFlags.value;
    }

    // explicitly declare FeatureFlags to avoid javascript type errors
    public deserializeFeatureFlags(data: any): FeatureFlags {
        const flags = new FeatureFlags();
        flags.uuid = data.uuid;
        flags.notification_center_flag = data.notification_center_flag;
        return flags;
    }

    public refreshFeatureFlags() {
        this.getFeatureFlags();
    }
}
