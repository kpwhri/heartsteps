import { Component, Output, EventEmitter } from '@angular/core';
import { NotificationService } from '@heartsteps/notifications/notification.service';
import { LoadingService } from '@infrastructure/loading.service';

@Component({
    selector: 'heartsteps-notifications-permission',
    templateUrl: 'notifications.html',
})
export class NotificationsPermission {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private notificationService: NotificationService,
        private loadingService:LoadingService
    ) {}

    getPermission() {
        this.loadingService.show("Getting permission")
        this.notificationService.enable()
        .then(() => {
            this.loadingService.dismiss()
            this.saved.emit(true);
        })
        .catch(() => {
            this.loadingService.dismiss()
            console.log('No permission')
        })
    }
}
