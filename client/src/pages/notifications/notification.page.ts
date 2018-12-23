import { Component, ElementRef, Renderer2, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import { Notification } from "@heartsteps/notifications/notification.model";
import { NotificationService } from "@heartsteps/notifications/notification.service";

@Component({
    selector: 'heartsteps-notification-page',
    templateUrl: './notification.page.html'
})
export class NotificationPage implements OnInit {

    private notification:Notification;

    constructor(
        private el:ElementRef,
        private renderer:Renderer2,
        private router: Router,
        private route: ActivatedRoute,
        private notificationService: NotificationService
    ) {}

    ngOnInit() {
        const notificationId = this.route.snapshot.paramMap.get('notificationId');
        this.notificationService.getNotification(notificationId)
        .then((notification:Notification) => {
            this.notification = notification;
        }).catch(() => {
            this.notification = new Notification(
                notificationId,
                "Example title",
                "This is an example notification message."
            )
        })

        this.renderer.addClass(this.el.nativeElement, 'start-screen');
    }

    public dismiss() {
        this.router.navigate(['']);
    }

}
