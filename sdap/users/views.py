from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import redirect

from sdap.users.models import Notification
from sdap.studies.models import ExpressionStudy, GeneList
from sdap.studies.views import check_view_permissions, paginate

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        groups = self.request.user.groups.all()

        context['groups'] = paginate(groups, self.request.GET.get('groups'))
        context['notifications'] = paginate(Notification.objects.filter(user=self.request.user), self.request.GET.get('notifications'))
        context['studies'] = paginate([study for study in ExpressionStudy.objects.all() if check_view_permissions(self.request.user, study, True)], self.request.GET.get('studies'))
        context['gene_lists'] = paginate(GeneList.objects.filter(created_by=self.request.user), self.request.GET.get('gene_lists'))

        for group in context['groups']:
            group.members_number = group.user_set.count()

        context['in_use'] = {
            'user': "",
            'notification': "",
            'group': "",
            'study': "",
            'gene_list': ""
        }

        if self.request.GET.get('notifications'):
            context['in_use']['notification'] = 'active'
        elif self.request.GET.get('studies'):
            context['in_use']['study'] = 'active'
        elif self.request.GET.get('groups'):
            context['in_use']['group'] = 'active'
        elif self.request.GET.get('gene_list'):
            context['in_use']['gene_list'] = 'active'
        else:
            context['in_use']['user'] = 'active'

        return context

user_detail_view = UserDetailView.as_view()


class UserListView(LoginRequiredMixin, ListView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_list_view = UserListView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name", "last_name", "institut"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()

class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


def dismiss_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    if not request.user == notification.user:
        return redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        notification.delete()
        data = {'form_is_valid': True, 'redirect': reverse("users:detail", kwargs={"username": request.user.username}) + "?notification=true"}
    else:
       context = {'group': notification.group, 'notification': notification}
       data['html_form'] = render_to_string('users/partial_notif_dismiss.html',
           context,
           request=request,
       )
    return JsonResponse(data)


def accept_group_invitation(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    # Check group is set
    if not notification.group:
        # Need a better redirection, though this should not happen
        notification.delete()
        return redirect('/unauthorized')

    if not request.user == notification.user:
        return redirect('/unauthorized')

    if not request.user in notification.group.user_set.all():
        notification.group.user_set.add(request.user)

    notification.delete()
    data = {'form_is_valid': True, 'redirect': reverse("users:detail", kwargs={"username": request.user.username}) + "?notification=true"}
    return JsonResponse(data)
