NewRawConfigParser
==================

重写了Python ConfigParser类中的RawConfigParser类，支持保留原配置文件中注释信息，支持添加新option到section最后，支持格式化输出option及value以实现“=”对齐。

使用方法：
git clone https://github.com/xinyu7git/NewRawConfigParser.git 到自己code目录。

支持环境：
1.代码中使用了OrderedDict作为_default_dict 类型，既from collections import OrderedDict as _default_dict ，故collections包中必须包含OrderedDict，否则无法使用。
（是由于本代码中引入了记录数据位置的self._location字典，set方法中会通过顺序遍历该字典，故该字典必须按照value值排序，所以使用了OrderedDict，当然若没有OrderedDict方法，可以自行改写set函数，通过排序的方式获取所需的localtion_index值。

2.Python环境需要包含re及原ConfigParser包。
3.支持原ConfigParser的allow_no_value方法，允许配置文件中option的value为空。
4.新支持一个参数new_option_len，默认不用输入，该参数用来控制option与“=”之间的距离，用以保证“=”对齐。

代码对比：
1.新添加一个列表self._data保存配置文件的各行信息，每行以字符串的形式存在该列表中，从第一行到最后一行，按顺序存储。
2.新添加一个字典self._location 保存所有section 及option 与self._data 的对应关系，key值为section或section+option，value为该setion或option在self_data中是索引位置。
3.新添加一个遍历new_option_len ,用户可以自定义输入，该参数用来控制option与“=”之间的距离，用以保证“=”对齐，仅仅起到美观的作用，默认为1，当该值小于option本身的长度时，option与“=”之间会自动保留一个空格。

重写函数：
1.def _read(self, fp, fpname):
读取文件的时候，会把每一行信息存储在self._data列表中，section及option的索引存在self._location 中。
2.def set(self, section, option, value=None):
支持原有功能，需要修改self._location及self._data,新插入的option默认位置在该section的最后一个非‘\n’行。支持option无value。
3.def add_section(self, section):
支持原有功能，添加section的时候需要修改self._location及self._data,新插入的section默认在最后一行，会保证与上一个section的最后一个option之间有一个空行。当插入的section为第一个section时，会默认在第一行输入“#A new config”注释。
4.def write(self, fp):
修改原有逻辑，只按照self._data中的数据输出即可。
5.def remove_option(self,section,option):
支持原有功能，删除option的时候，需要修改self._location及self._data。
6.def remove_section(self,section):
支持原有功能，删除section的时候，循环删除该section下的所有option，最后删除该section自己。
