from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from .models import Recipe, Comment, CuisineTag, IngredientTag
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RecipeForm
from django.views.generic.edit import UpdateView, DeleteView
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.contrib.auth import views as auth_views


class Home(generic.ListView):
    queryset = Recipe.objects.order_by("-date_created")
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        with open('myrecipes/welcome_text.txt', 'r') as file:
            welcome_text = file.readlines()

        context = super().get_context_data(**kwargs)
        context['top_recipes'] = Recipe.objects.order_by('-likes')[:5]
        context['welcome_text'] = welcome_text
        return context


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context


class CustomLogoutView(LogoutView):
    next_page = 'home'


class CustomSignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        self.object.username = username
        self.object.email = email
        self.object.save()
        return response


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        response = super().form_valid(form)

        # You can customize the email sent to the user here
        user = form.cleaned_data['email']
        # Send the email using your preferred email sending method

        return response


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by("-date_created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_recipes = self.get_queryset()
        context['user_recipes'] = user_recipes

        return context


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'upload_recipe.html'
    success_url = '/'  # Replace with the desired URL after successful submission

    def form_valid(self, form):
        form.instance.author = self.request.user

        # Handle uploaded image
        image_file = self.request.FILES.get('image')
        if image_file:
            form.instance.image = image_file

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            image_file = self.request.FILES.get('image')
            if image_file and hasattr(image_file, 'url'):
                context['image_url'] = image_file.url
            else:
                context['image_url'] = None
        else:
            context['image_url'] = None
        return context


class EditRecipeView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'edit_recipe.html'
    success_url = reverse_lazy('account')

    def form_valid(self, form):
        form.instance.author = self.request.user

        # Handle uploaded image
        image_file = self.request.FILES.get('image')
        if image_file:
            form.instance.image = image_file

        # Check if the image should be removed
        remove_image = form.data.get('remove_image', False)
        if remove_image:
            # Remove the image file from storage and clear the image field
            form.instance.image.delete()
            form.instance.image = None

        return super().form_valid(form)


class DeleteRecipeView(LoginRequiredMixin, View):
    def form_valid(self, form):
        # Check if the "image" field is cleared in the form
        if form.cleaned_data['image'] is None:
            # Delete the old image from the database
            recipe = form.instance
            recipe.image.delete(save=False)

        return super().form_valid(form)

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.author != request.user:
            # Handle unauthorized deletion attempt
            # Redirect to an appropriate page or return an error message
            pass

        recipe.delete()
        return redirect('account')


class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = 'recipe_detail.html'


class BrowseRecipes(generic.ListView):
    queryset = Recipe.objects.order_by("-date_created")
    template_name = "browse_recipes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipes = context["object_list"]
        context['recipes'] = recipes

        return context


class AddCommentView(View):
    def post(self, request, pk):
        recipe = Recipe.objects.get(id=pk)
        content = request.POST.get('content')
        author = request.user
        Comment.objects.create(recipe=recipe, content=content, author=author)
        return redirect('recipe_detail', pk=pk)


class LikeRecipeView(View):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if user.is_authenticated:
            if user in recipe.likes.all():
                recipe.likes.remove(user)  # Unlike the recipe
            else:
                recipe.likes.add(user)  # Like the recipe
            # Additional logic if needed

        return redirect('recipe_detail', pk=pk)


class SearchRecipeView(TemplateView):
    template_name = 'search_recipes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title_filter = self.request.GET.get('title', '').lower()
        cuisines_filter = self.request.GET.get('types', '').lower()
        ingredients_filter = self.request.GET.get('ingredients', '').lower()

        recipes = Recipe.objects.order_by("-date_created")

        if title_filter:
            recipes = recipes.filter(title__icontains=title_filter)

        if cuisines_filter:
            cuisines = [cuisine.strip().lower() for cuisine in cuisines_filter.split(',') if cuisine.strip()]
            for cuisine in cuisines:
                recipes = recipes.filter(cuisines_tag__name__icontains=cuisine)

        if ingredients_filter:
            ingredients = [ingredient.strip().lower() for ingredient in ingredients_filter.split(',') if
                           ingredient.strip()]
            for ingredient in ingredients:
                recipes = recipes.filter(ingredient_tag__name__icontains=ingredient)

        context['recipes'] = recipes
        return context


class CommentDeleteView(DeleteView):
    model = Comment

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('recipe_detail', kwargs={'pk': self.object.recipe.pk})


class ChangePasswordView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = '/account/'  # Update the URL to redirect after password change


class ContactUsView(View):
    def get(self, request):
        return render(request, 'contact_us.html')

    def post(self, request):
        email = request.POST.get('email')
        title = request.POST.get('title')
        message = request.POST.get('message')

        subject = f"[{title}] - {email}"
        body = f"""
        From: {email}
        Message: {message}
        """
        send_mail(subject, body, 'app2023myrecipes@gmail.com', ['app2023myrecipes@gmail.com'])

        return redirect('contact_us_success')


class ContactUsSuccessView(View):
    def get(self, request):
        return render(request, 'contact_us_success.html')


class AboutView(TemplateView):
    template_name = 'about.html'



