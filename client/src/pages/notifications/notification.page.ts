import { Component, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageService } from "@heartsteps/notifications/message.service";

@Component({
    selector: 'heartsteps-notification-page',
    templateUrl: './notification.page.html'
})
export class NotificationPage implements OnInit {
    private notification: Message;

    public title: string;
    public body: string;

    constructor(
        private router: Router,
        private activatedRoute: ActivatedRoute,
        private messageService: MessageService
    ) {}

    ngOnInit() {
        console.log('NotficationPage: Intialized');
        this.activatedRoute.paramMap.subscribe((paramMap) => {
            const notificationId: string = paramMap.get('notificationId');
            console.log('NotficationPage: Loading notification id=' + notificationId);
            this.messageService.getMessage(notificationId)
            .then((notification) => {
                this.notification = notification;
                console.log('NotificationPage: Loaded notification id='+this.notification.id);
                this.title = this.notification.title;
                this.body = this.notification.body;
            })
        });
    }

    public dismiss() {
        this.notification.engaged();
        this.router.navigate(['']);
    }

}
