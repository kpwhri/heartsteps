import { Component, OnInit } from "@angular/core";
import { MessageService } from "@heartsteps/notifications/message.service";
import { Router } from "@angular/router";
import { LoadingService } from "@infrastructure/loading.service";



@Component({
    templateUrl: './notifications.page.html'
})
export class NotificationsPage implements OnInit {

    public notificationsEnabled:boolean;

    constructor(
        private loadingService: LoadingService,
        private messageService: MessageService,
        private router: Router
    ) {}

    ngOnInit() {
        this.messageService.isEnabled()
        .then(() => {
            this.notificationsEnabled = true;
        })
        .catch(() => {
            this.notificationsEnabled = false;
        });
    }

    public disableNotifications() {
        this.loadingService.show('Disabling notifications');
        this.messageService.disable()
        .then(() => {

        })
        .catch(() => {
            // show error message?
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public enableNotifications() {
        this.loadingService.show('Enabling notifications');
        this.messageService.enable()
        .then(() => {

        })
        .catch((e) => {
            console.log("NotificationPage: Can't enable notifications", e);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

}
