import { Component, OnInit, OnDestroy } from "@angular/core";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Message } from "@heartsteps/notifications/message.model";
import { Subscription } from "rxjs";

@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html",
})
export class NotificationCenterPage implements OnInit, OnDestroy {
    public notifications: Message[] = [];
    public haveUnread: boolean = false;
    public featureFlags: FeatureFlags;

    private unreadStatusSubscription: Subscription;
    private notificationsSubscription: Subscription;

    private featureFlagSubscription: Subscription;

    constructor(
        private notificationCenterService: NotificationCenterService,
        private featureFlagService: FeatureFlagService
    ) {}

    // redirects message based on message.type
    public redirect(notification: Message) {
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
        this.notificationCenterService.refreshNotifications();
    }

    ngOnDestroy() {
        this.notificationCenterService.updateAllNotifications();
        this.notificationsSubscription.unsubscribe();
        this.unreadStatusSubscription.unsubscribe();
        this.featureFlagSubscription.unsubscribe();
    }
}
