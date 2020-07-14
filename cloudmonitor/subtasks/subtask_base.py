class SubTaskBase:

    def run(self, context):
        raise NotImplementedError()

    def run_supported(self):
        return self.__class__.run != SubTaskBase.run
