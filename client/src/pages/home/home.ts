import {
    Component,
    OnInit,
    OnDestroy,
    ElementRef,
    ViewChild,
} from "@angular/core";
import { Router, RouterEvent, NavigationEnd } from "@angular/router";
import { Subscription } from "rxjs";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { BackgroundMode } from '@ionic-native/background-mode/ngx';

class Tab {
    name: string;
    key: string;
}

@Component({
    selector: "page-home",
    templateUrl: "home.html",
})
export class HomePage implements OnInit, OnDestroy {
    @ViewChild("#home-container") container: ElementRef;

    public pageTitle: string;
    public activeTab: string;
    public backButton: boolean;

    public updatingParticipant: boolean;
    public updatingParticipantSubscription: Subscription;

    private routerSubscription: Subscription;
    private notificationCenterUrl = "/home/notification-center";
    private notificationCenterName = "Notification Center";

    private unreadStatusSubscription: Subscription;
    public haveUnread: boolean = true;
    
    private offlineStatusSubscription: Subscription;
    public offlineStatus: boolean = false;

    private featureFlagSubscription: Subscription;
    public featureFlags: FeatureFlags;

    public tabs: Array<Tab> = [
        {
            name: "Dashboard",
            key: "dashboard",
        },
        {
            name: "Planning",
            key: "planning",
        },
        {
            name: "Activities",
            key: "activities",
        },
        {
            name: "Settings",
            key: "settings",
        },
    ];

    constructor(
        private router: Router,
        private element: ElementRef,
        private participantService: ParticipantService,
        private notificationCenterService: NotificationCenterService,
        private featureFlagService: FeatureFlagService,
        public backgroundMode: BackgroundMode
    ) {}

    ngOnInit() {
        this.backgroundMode.enable();
        this.updateFromUrl(this.router.url);
        this.routerSubscription = this.router.events
            .filter((event) => event instanceof NavigationEnd)
            .subscribe((event: RouterEvent) => {
                this.updateFromUrl(event.url);
            });
        this.updatingParticipantSubscription =
            this.participantService.updatingParticipant.subscribe(
                (isUpdating) => {
                    this.updatingParticipant = isUpdating;
                }
            );
        this.unreadStatusSubscription =
            this.notificationCenterService.currentUnreadStatus.subscribe(
                (unreadStatus) => (this.haveUnread = unreadStatus)
            );

        this.offlineStatusSubscription =
            this.notificationCenterService.currentOfflineStatus.subscribe(
                (offlineStatus) => (this.offlineStatus = offlineStatus)
            );

        this.featureFlagSubscription =
            this.featureFlagService.currentFeatureFlags.subscribe(
                (flags) => (this.featureFlags = flags)
            );

        this.notificationCenterService.refreshNotifications();
    }

    ngOnDestroy() {
        this.routerSubscription.unsubscribe();
        this.updatingParticipantSubscription.unsubscribe();
        this.unreadStatusSubscription.unsubscribe();
        this.offlineStatusSubscription.unsubscribe();
        this.featureFlagSubscription.unsubscribe();
    }

    private updateFromUrl(url: string) {
        this.getActiveTab(url)
            .then((activeTab: Tab) => {
                if (this.activeTab !== activeTab.key) {
                    this.element.nativeElement.querySelector(
                        "#home-content"
                    ).scrollTop = 0;
                }
                this.pageTitle = activeTab.name;
                this.activeTab = activeTab.key;
            })
            .catch(() => {
                if (url === this.notificationCenterUrl) {
                    this.pageTitle = this.notificationCenterName;
                } else {
                    console.log("No matching tab found");
                }
            });
    }

    private getActiveTab(url: string): Promise<Tab> {
        return new Promise((resolve, reject) => {
            const matchingTab = this.tabs.find((tab) => {
                return url.indexOf(tab.key) >= 0;
            });

            if (matchingTab) {
                resolve(matchingTab);
            } else {
                reject("No matching tab");
            }
        });
    }
    
    public notificationCenterFlag(): boolean {
        // console.log("home.ts notification center flag called");
        return this.featureFlagService.hasFlagNP("notification_center");
    }

    public offlineStatusIconFlag(): boolean {
        return this.featureFlagService.hasFlagNP("offline_status_icon");
    }
}
