import { Component, OnDestroy } from "@angular/core";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import * as moment from "moment";
import { Platform } from "ionic-angular";
import { Subscription } from "rxjs";
import { CurrentWeekService } from "@heartsteps/current-week/current-week.service";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { AnchorMessageService } from "@heartsteps/anchor-message/anchor-message.service";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { skip } from "rxjs/operators";

@Component({
    templateUrl: "dashboard.page.html",
})
export class DashboardPage implements OnDestroy {
    public today: Date;
    public formattedDate: string;
    public summary: DailySummary;

    public weeklyGoal: number;

    public anchorMessage: string;
    public featureFlags: FeatureFlags;

    private resumeSubscription: Subscription;
    private featureFlagSubscription: Subscription;

    constructor(
        private anchorMessageService: AnchorMessageService,
        private dailySummaryService: DailySummaryService,
        private currentWeekService: CurrentWeekService,
        // tslint:disable-next-line:no-unused-variable
        private participantService: ParticipantService,
        private platform: Platform,
        private featureFlagService: FeatureFlagService
    ) {
        this.today = new Date();
        this.formattedDate = moment().format("dddd, M/D");

        this.dailySummaryService.watch(this.today).subscribe((summary) => {
            this.summary = summary;
        });
        this.currentWeekService.week
            .filter((week) => week !== undefined)
            .subscribe((week) => {
                this.weeklyGoal = week.goal;
            });
        this.resumeSubscription = this.platform.resume.subscribe(() => {
            this.update();
        });

        this.update();
    }

    public update() {
        this.updateAnchorMessage();
        this.dailySummaryService.updateCurrentWeek();
    }

    private updateAnchorMessage() {
        this.anchorMessageService
            .get()
            .then((message) => {
                this.anchorMessage = message;
            })
            .catch(() => {
                this.anchorMessage = undefined;
            });
    }

    public hasFlag(flag: string): boolean {
        return this.featureFlagService.hasFlag(flag);
    }

    ngOnInit() {
        this.featureFlagSubscription =
            this.featureFlagService.currentFeatureFlags
                .pipe(skip(1))
                .subscribe((flags) => (this.featureFlags = flags));
    }

    ngOnDestroy() {
        if (this.resumeSubscription) {
            this.resumeSubscription.unsubscribe();
        }
        if (this.featureFlagSubscription) {
            this.featureFlagSubscription.unsubscribe();
        }
    }
}
