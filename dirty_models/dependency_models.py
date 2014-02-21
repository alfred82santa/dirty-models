"""
dependency_models.py

All the DependencyModels models, functions, types and fields
"""

from .fields import BaseField, ModelField, ArrayField
from dirty_models.fields import IntegerField, FloatField, BooleanField, StringField, DateTimeField
from datetime import datetime
from dirty_models.types import ListModel
from .models import BaseModel, DirtyModelMeta



def get_dependencies_from_dependency_string(dependency_string):
        dependency_splits = dependency_string.split('.')
        own_field = dependency_splits[0]
        if len(dependency_splits) > 1:
            return own_field, ''.join(dependency_splits[1:])
        return own_field, None



class DependencyListModel(ListModel):

    """
    ListModel object to be compatible with DependencyModels
    """

    # TODO: the rest of functions of ListModel should also call the force_parent_modified and maybe clear son's dependencies

    def __init__(self, seq=None, field_type=None):
        self.other_dependencies = {}
        self.direct_dependencies = {}
        super(DependencyListModel, self).__init__(seq, field_type)

    def set_dependency_received(self, dependency, field, parent_object):
        """
        Manages the dependencies that are directly related to objects saved in the array
        """
        if not field in self.other_dependencies:
            self.other_dependencies[field] = {}
        if not parent_object in self.other_dependencies[field]:
            self.other_dependencies[field][parent_object] = set()
        self.other_dependencies[field][parent_object].add(dependency)
        for model in self:
            model.set_dependency_received(dependency, field, parent_object)

    def add_direct_dependency(self, parent_object, dependency_name):
        """
        Saves the dependencies that are direct to the entire array
        """
        if not parent_object in self.direct_dependencies:
            self.direct_dependencies[parent_object] = set()
        self.direct_dependencies[parent_object].add(dependency_name)

    def send_all_dependencies_saved(self, model_object):
        """
        Send dependencies to the son's
        """
        if isinstance(model_object, (ArrayField, ModelField)):
            for field, dependency in self.other_dependencies.items():
                for parent_object, dependency_key in dependency:
                    model_object.set_dependency_received(dependency_key, field, parent_object)

    def force_parent_modified(self, object_to_trigger_modification):
        """
        Tells the parent to modify the dependent fields
        """
        for parent_object, dependencies in self.direct_dependencies.items():
            for dependency in dependencies:
                if isinstance(self.field_type, ModelField):
                    if object_to_trigger_modification.get_field_value(dependency.split('.')[-1]):
                        parent_object.force_modified_by_dependency_key(dependency)
                elif isinstance(self.field_type, ArrayField):
                    for array_object in object_to_trigger_modification:
                        self.force_parent_modified(array_object)
                else:
                    parent_object.force_modified_by_dependency_key(dependency)

    def append(self, item):
        super(DependencyListModel, self).append(item)
        self.send_all_dependencies_saved(item)
        self.force_parent_modified(item)

    def insert(self, index, p_object):
        super(DependencyListModel, self).insert(index, p_object)
        self.send_all_dependencies_saved(p_object)
        self.force_parent_modified(p_object)

    def force_modified(self, name):
        """
        Forces modification of the sons
        """
        if not isinstance(self.field_type, (ArrayField, ModelField)):
            raise Exception("Dependency arrived to the array is not valid")
        for list_object in self:
            list_object.force_modified(name)


class DependencyArrayField(ArrayField):

    """
    ArrayField with the same behaviour but using DependencyListModel
    """

    def convert_value(self, value):
        def convert_element(element):
            """
            Helper to convert a single item
            """
            if not self.field_type.check_value(element) and self._field_type.can_use_value(element):
                return self.field_type.convert_value(element)
            return element
        return DependencyListModel([convert_element(element) for element in value], field_type=self.field_type)


class DependencyDirtyModelMeta(DirtyModelMeta):

    def __new__(cls, name, bases, classdict):
        result = super(DependencyDirtyModelMeta, cls).__new__(cls, name, bases, classdict)
        array_fields = {key: field for key, field in result.__dict__.items() if isinstance(field, ArrayField)}
        for key, field in array_fields.items():
            setattr(result, key, DependencyArrayField(field.name, field.field_type))
        return result


class DependencyBaseModel(BaseModel, metaclass=DependencyDirtyModelMeta):

    dependencies = ()

    def __init__(self, data=None, **kwargs):
        super(DependencyBaseModel, self).__init__(data, **kwargs)
        self.set_dependency_tree()
        self.other_models_dependencies = {}

    def set_dependency_tree(self):
        self.dependency_tree = {}
        self.dependency_tree_own_fields = {}
        for dependency_tuple in self.dependencies:
            own_fields = []
            for dependent_field in dependency_tuple:
                if not self.dependency_tree.get(dependent_field):
                    self.dependency_tree[dependent_field] = set()
                self.dependency_tree[dependent_field] = self.dependency_tree[dependent_field].union(set(dependency_tuple))
                self.dependency_tree[dependent_field].remove(dependent_field)
                own_field, son_field = get_dependencies_from_dependency_string(dependent_field)
                own_fields.append(own_field)
            for field in own_fields:
                if not self.dependency_tree_own_fields.get(field):
                    self.dependency_tree_own_fields[field] = set()
                self.dependency_tree_own_fields[field] = self.dependency_tree_own_fields[field].union(set(own_fields))
                self.dependency_tree_own_fields[field].remove(field)

    def send_dependencies(self, dependencies, model):
        # It is possible to arrive here if the model is a ArrayField or a BaseField
        for dependency in dependencies:
            own_field, descendent_field = get_dependencies_from_dependency_string(dependency)
            model.set_dependency_received(dependency, descendent_field, self)
            if isinstance(model, DependencyListModel):
                model.add_direct_dependency(self, dependency)

    def set_dependency_received(self, dependency, field, parent_object):
        own_field, descendent_field = get_dependencies_from_dependency_string(field)
        if not descendent_field:
            if not self.other_models_dependencies.get(own_field):
                self.other_models_dependencies[own_field] = {}
            if not self.other_models_dependencies[own_field].get(parent_object):
                self.other_models_dependencies[own_field][parent_object] = []
            self.other_models_dependencies[own_field][parent_object].append(dependency)
        else:
            self.get_field_value(own_field).set_dependency_received(dependency, descendent_field, parent_object)

    def force_modified_by_dependency_key(self, name):
        self.force_modified(name)
        for dependency_name in self.dependency_tree.get(name, []):
            self.force_modified(dependency_name)

    def force_modified(self, name):
        own_field, descendent_field = get_dependencies_from_dependency_string(name)
        if not descendent_field:
            descendent_object = self.get_field_value(name)
            if isinstance(descendent_object, DependencyBaseModel):
                # When is about ModelField, set_field_value is not invoked
                object_dict = descendent_object._original_data.copy()
                object_dict.update(descendent_object._modified_data)
                descendent_object._original_data.clear()
                descendent_object._modified_data = object_dict
            else:
                if descendent_object:
                    self._set_field_value(name, descendent_object, forced_update=True)
        else:
            self.get_field_value(own_field).force_modified(descendent_field)

    def get_indirect_dependencies_between_fields(self, field_origin, field_dest):
        if field_dest not in self.dependency_tree_own_fields.get(field_origin, []):
            return []
        dependencies = self.dependency_tree.get(field_origin, [])
        return [dependency for dependency in dependencies if dependency.startswith(field_dest + '.')]


    def manage_own_dependencies(self, field_name, value):
        # TODO: Analyse if it is necessary to send value or not
        if self.dependency_tree_own_fields.get(field_name):
            dependent_fields = self.dependency_tree_own_fields[field_name]
            for dependent_field in dependent_fields:
                if self.get_field_value(dependent_field):
                    if field_name in self.dependency_tree.get(dependent_field, []):
                        # direct relationship between fields
                        self.force_modified(dependent_field)
                    else:
                        indirect_relationships_to_modify = self.get_indirect_dependencies_between_fields(field_name, dependent_field)
                        if not indirect_relationships_to_modify:
                            self.force_modified(dependent_field)
                        for relationship in indirect_relationships_to_modify:
                            self.force_modified(relationship)
                        self.send_dependencies(self.get_indirect_dependencies_between_fields(dependent_field, field_name), value)

    def manage_other_models_dependencies(self, field_name):
        if self.other_models_dependencies.get(field_name):
            for parent_object in self.other_models_dependencies[field_name]:
                for dependency in self.other_models_dependencies[field_name].get(parent_object, []):
                    parent_object.force_modified_by_dependency_key(dependency)

    def _set_field_value(self, name, value, forced_update=False):
        if name in self._deleted_fields:
            self._deleted_fields.remove(name)
        if self._original_data.get(name) == value and not forced_update:
            if self._modified_data.get(name):
                self._modified_data.pop(name)
        else:
            self._modified_data[name] = value

    def set_field_value(self, name, value):
        self.manage_own_dependencies(name, value)
        self.manage_other_models_dependencies(name)
        self._set_field_value(name, value)