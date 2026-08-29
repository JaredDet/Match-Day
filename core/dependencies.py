import injector


class CoreModule(injector.Module):
    """Bindings compartidos por todos los módulos de la aplicación."""

    def configure(self, binder: injector.Binder) -> None:
        pass
