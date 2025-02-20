from Database.dbs import db

class Detection(db.Model):
    __tablename__ = 'detection'

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    camera = db.Column(db.Integer)
    inout1 = db.Column(db.String(10))
    remark = db.Column(db.String(100))
    one = db.Column(db.Integer)
    two = db.Column(db.Integer)
    three = db.Column(db.Integer)
    four = db.Column(db.Integer)
    five = db.Column(db.Integer)
    six = db.Column(db.Integer)
    seven = db.Column(db.Integer)
    eight = db.Column(db.Integer)
    nine = db.Column(db.Integer)
    ten = db.Column(db.Integer)
    eleven = db.Column(db.Integer)
    twelve = db.Column(db.Integer)
    thirteen = db.Column(db.Integer)
    fourteen = db.Column(db.Integer)
    fifteen = db.Column(db.Integer)
    sixteen = db.Column(db.Integer)
    seventeen = db.Column(db.Integer)
    eighteen = db.Column(db.Integer)
    nineteen = db.Column(db.Integer)
    twenty = db.Column(db.Integer)
    twentyone = db.Column(db.Integer)
    twentytwo = db.Column(db.Integer)
    twentythree = db.Column(db.Integer)
    twentyfour = db.Column(db.Integer)




    def __init__(self,id=None,date=None, camera=None, inout1=None, remark=None, one=None, two=None, three=None,
                 four=None, five=None, six=None, seven=None, eight=None, nine=None, ten=None, eleven=None,
                 twelve=None, thirteen=None, fourteen=None, fifteen=None, sixteen=None, seventeen=None,
                 eighteen=None, nineteen=None, twenty=None, twentyone=None, twentytwo=None, twentythree=None, twentyfour=None):
        self.id = id
        self.date = date
        self.camera = camera
        self.inout1 = inout1
        self.remark = remark
        self.one = one
        self.two = two
        self.three = three
        self.four = four
        self.five = five
        self.six = six
        self.seven = seven
        self.eight = eight
        self.nine = nine
        self.ten = ten
        self.eleven = eleven
        self.twelve = twelve
        self.thirteen = thirteen
        self.fourteen = fourteen
        self.fifteen = fifteen
        self.sixteen = sixteen
        self.seventeen = seventeen
        self.eighteen = eighteen
        self.nineteen = nineteen
        self.twenty = twenty
        self.twentyone = twentyone
        self.twentytwo = twentytwo
        self.twentythree = twentythree
        self.twentyfour = twentyfour



    def sum(self):
        # 获取每个属性的值，如果为 None 则置为 0
        one = self.one if self.one is not None else 0
        two = self.two if self.two is not None else 0
        three = self.three if self.three is not None else 0
        four = self.four if self.four is not None else 0
        five = self.five if self.five is not None else 0
        six = self.six if self.six is not None else 0
        seven = self.seven if self.seven is not None else 0
        eight = self.eight if self.eight is not None else 0
        nine = self.nine if self.nine is not None else 0
        ten = self.ten if self.ten is not None else 0
        eleven = self.eleven if self.eleven is not None else 0
        twelve = self.twelve if self.twelve is not None else 0
        thirteen = self.thirteen if self.thirteen is not None else 0
        fourteen = self.fourteen if self.fourteen is not None else 0
        fifteen = self.fifteen if self.fifteen is not None else 0
        sixteen = self.sixteen if self.sixteen is not None else 0
        seventeen = self.seventeen if self.seventeen is not None else 0
        eighteen = self.eighteen if self.eighteen is not None else 0
        nineteen = self.nineteen if self.nineteen is not None else 0
        twenty = self.twenty if self.twenty is not None else 0
        twentyone = self.twentyone if self.twentyone is not None else 0
        twentytwo = self.twentytwo if self.twentytwo is not None else 0
        twentythree = self.twentythree if self.twentythree is not None else 0
        twentyfour = self.twentyfour if self.twentyfour is not None else 0

        # 对属性值进行求和
        return one + two + three + four + five + six + seven + eight + nine + ten + eleven + \
            twelve + thirteen + fourteen + fifteen + sixteen + seventeen + eighteen + nineteen + \
            twenty + twentyone + twentytwo + twentythree + twentyfour

    def get_all_data(self):
        return [self.one, self.two, self.three, self.four, self.five, self.six, self.seven, self.eight,
                self.nine, self.ten, self.eleven, self.twelve, self.thirteen, self.fourteen, self.fifteen,
                self.sixteen, self.seventeen, self.eighteen, self.nineteen, self.twenty, self.twentyone,
                self.twentytwo, self.twentythree, self.twentyfour]

    def __getitem__(self, item):
        return getattr(self, item)
    def __repr__(self):
        return f'<Detection {self.one, self.two, self.three, self.four, self.five, self.six, self.seven, self.eight,self.nine, self.ten, self.eleven, self.twelve, self.thirteen, self.fourteen, self.fifteen,self.sixteen, self.seventeen, self.eighteen, self.nineteen, self.twenty, self.twentyone,self.twentytwo, self.twentythree, self.twentyfour}>'

    def keys(self):
        return ( 'id', 'date', 'camera', 'inout1', 'remark', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'twentyone', 'twentytwo', 'twentythree', 'twentyfour')