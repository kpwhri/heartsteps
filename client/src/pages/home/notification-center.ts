import { Component, OnInit, OnDestroy } from "@angular/core";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Message } from "@heartsteps/notifications/message.model";
import { Subscription } from "rxjs";

@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html"
})
export class NotificationCenterPage implements OnInit, OnDestroy {
    public notifications: Message[] = [];
    public haveUnread: boolean = false;
    public featureFlags: FeatureFlags;
    public notificationRefreshInterval: any;
    public featureFlagRefreshInterval: any;

    private unreadStatusSubscription: Subscription;
    private notificationsSubscription: Subscription;

    private featureFlagSubscription: Subscription;

    constructor(
        private notificationCenterService: NotificationCenterService,
        private featureFlagService: FeatureFlagService
    ) {}

    // redirects message based on message.type
    public redirect(notification: Message) {
        // TODO: so far only tested message.type == "notification", test other types
        return this.notificationCenterService.redirectNotification(
            notification
        );
    }

    public isReceived(notification: Message): boolean {
        return this.notificationCenterService.isReceived(notification);
    }

    public isRead(notification: Message): boolean {
        return this.notificationCenterService.isRead(notification);
    }

    ngOnInit() {
        this.notificationsSubscription =
            this.notificationCenterService.currentNotifications.subscribe(
                (notifications) => (this.notifications = notifications)
            );
        this.unreadStatusSubscription =
            this.notificationCenterService.currentUnreadStatus.subscribe(
                (unreadStatus) => (this.haveUnread = unreadStatus)
            );

        this.featureFlagSubscription =
            this.featureFlagService.currentFeatureFlags.subscribe(
                (flags) => (this.featureFlags = flags)
            );
        /* 
        TODO: bug where refreshNotification is called twice and only updates every other call
        bell icon updates 2.5 sec too late after data already arrives in inbox, should be synced
        problem is that i'm subscribing twice (here and home.ts)
        but i need to subscribe here to render HTML template
        and i need to subscribe on home.ts to get updated readStatus
        need to make notification-center.ts into own component to fix 
        */
        this.notificationCenterService.refreshNotifications();
        this.notificationRefreshInterval = setInterval(() => {
            this.notificationCenterService.refreshNotifications();
        }, 5000);

        this.featureFlagRefreshInterval = setInterval(() => {
            this.featureFlagService.refreshFeatureFlags();
        }, 10000);
    }

    ngOnDestroy() {
        clearInterval(this.notificationRefreshInterval);
        clearInterval(this.featureFlagRefreshInterval);
        this.notificationCenterService.updateAllNotifications();
        this.notificationsSubscription.unsubscribe();
        this.unreadStatusSubscription.unsubscribe();
        this.featureFlagSubscription.unsubscribe();
    }
}
