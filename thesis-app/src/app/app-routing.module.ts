import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IssuesComponent } from './issues/issues.component';
import { SelectedIssuesComponent } from './selected-issues/selected-issues.component';

const routes: Routes = [
  { path: '', component: IssuesComponent },
  { path: 'selected', component: SelectedIssuesComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
