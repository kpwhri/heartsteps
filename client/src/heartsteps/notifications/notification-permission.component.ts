import { Component, Output, EventEmitter } from '@angular/core';
import { MessageService } from '@heartsteps/notifications/message.service';
import { LoadingService } from '@infrastructure/loading.service';

@Component({
    selector: 'heartsteps-notifications-permission',
    templateUrl: 'notification-permission.component.html',
})
export class NotificationsPermissionComponent {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private messageService: MessageService,
        private loadingService:LoadingService
    ) {}

    public getPermission() {
        this.loadingService.show("Getting permission")
        this.messageService.enable()
        .then(() => {
            this.saved.emit(true);
        })
        .catch(() => {
            console.log('No permission 2');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public skip() {
        this.messageService.disable()
        .then(() => {
            this.saved.emit();
        });
    }
}
