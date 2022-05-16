# coding=utf-8
import sys, os
reload(sys)
sys.setdefaultencoding('utf8')
class Const(object):

    ROOT_PATH = os.path.dirname(__file__) + '/../'
    CONF_PATH = os.path.dirname(__file__) + '/../config/'
    DB_PATH = os.path.dirname(__file__) + '/../db/'
    DATA_PATH = os.path.dirname(__file__) + '/../data/'
    LOG_PATH = os.path.dirname(__file__) + '/../log/'
    RESOURCE_PATH = os.path.dirname(__file__) + '/../resource/'

    class ConstError(TypeError):
        pass
    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't change const.%s" % name
        if not name.isupper():
            raise self.ConstCaseError, "Const name '%s' is not all uppercase" % name

        self.__dict__[name] = value

    def __delattr__(self, name):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't unbind const const instance attribute (%s)" % name

        raise AttributeError, "Const instance has no attribute '%s'" % name

    def _setattr_impl(self, name, value):
        raise self.ConstError, "Can't bind const instance attribute (%s)" % name