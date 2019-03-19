import { Component, Output, EventEmitter } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';

@Component({
  selector: 'fitbit-app-page',
  templateUrl: 'fitbit-app.html',
})
export class FitbitApp {
  @Output() saved = new EventEmitter<boolean>();

  constructor(
    private loadingService:LoadingService
  ) {}

  checkConnection() {
    this.loadingService.show("Checking connection")
    setTimeout(() => {
        this.loadingService.dismiss()
        this.saved.emit(true);
    }, 5000)
  }
}
